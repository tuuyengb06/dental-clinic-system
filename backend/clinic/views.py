import logging
import re
from decimal import Decimal
from urllib.parse import quote, urlencode

from django.conf import settings
from django.db.models import Q
from django.db import DatabaseError, IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from appointments.models import MedicalRecord
from .models import (
    ActiveInvoicePayment,
    BankTransferVerification,
    Doctor,
    Invoice,
    Patient,
    Payment,
    Service,
    Tooth,
    WorkSchedule,
)
from appointments.views import (
    AppointmentViewSet,
    IsAppointmentStaff,
    IsScheduleStaff,
    MedicalRecordViewSet,
)
from .serializers import (
    DoctorSerializer,
    DentalServiceSerializer,
    InvoiceCreateSerializer,
    InvoiceSerializer,
    InvoiceSourceSerializer,
    CashPaymentRequestSerializer,
    CancelQrPaymentSerializer,
    ManualQrReconciliationSerializer,
    PatientSerializer,
    PaymentSerializer,
    ToothSerializer,
    WorkScheduleSerializer,
)

logger = logging.getLogger(__name__)


class IsClinicAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return request.user and request.user.is_authenticated
        clinic_profile = getattr(request.user, "clinic_profile", None)
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_superuser
                or (clinic_profile and clinic_profile.role.code == "ADMIN")
            )
        )


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAppointmentStaff]

    def get_queryset(self):
        queryset = super().get_queryset()
        if "search" not in self.request.query_params:
            return queryset

        search_term = self.request.query_params["search"].strip()
        if not search_term:
            raise ValidationError({"search": "Enter a patient code, name, or phone number."})
        if len(search_term) > 100:
            raise ValidationError({"search": "Search must be 100 characters or fewer."})
        if not re.fullmatch(r"[\w\s.\-+'()]+", search_term, flags=re.UNICODE):
            raise ValidationError({"search": "Search contains unsupported characters."})
        return queryset.filter(
            Q(patient_code__icontains=search_term)
            | Q(full_name__icontains=search_term)
            | Q(phone__icontains=search_term)
        )


class ToothViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tooth.objects.all()
    serializer_class = ToothSerializer
    permission_classes = [IsAuthenticated]


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Doctor.objects.select_related("clinic_user__user", "clinic_user__role").all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]


class WorkScheduleViewSet(viewsets.ModelViewSet):
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer
    permission_classes = [IsScheduleStaff]

class DentalServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = DentalServiceSerializer
    permission_classes = [IsClinicAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        service = self.get_object()
        service.is_active = False
        service.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class IsBillingStaff(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        clinic_profile = getattr(user, "clinic_profile", None)
        return bool(
            clinic_profile
            and clinic_profile.role.code in ("ADMIN", "RECEPTIONIST")
        )


class InvoiceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsBillingStaff]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return Invoice.objects.select_related("patient").prefetch_related(
            "items__service",
            "payments__received_by__user",
            "payments__cancelled_by",
            "payments__verification__verified_by",
        ).order_by("-issued_at", "-id")

    def get_serializer_class(self):
        if self.action == "create":
            return InvoiceCreateSerializer
        if self.action == "available_records":
            return InvoiceSourceSerializer
        if self.action == "pay_cash":
            return CashPaymentRequestSerializer
        if self.action == "reconcile_qr":
            return ManualQrReconciliationSerializer
        if self.action == "cancel_qr":
            return CancelQrPaymentSerializer
        return InvoiceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            invoice = serializer.save()
        except IntegrityError as error:
            raise ValidationError(
                {"medical_record": "An invoice already exists for this examination record."}
            ) from error
        response_serializer = InvoiceSerializer(invoice, context=self.get_serializer_context())
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="available-records")
    def available_records(self, request):
        records = MedicalRecord.objects.filter(
            services__isnull=False,
            invoice__isnull=True,
        ).select_related(
            "appointment__patient"
        ).prefetch_related("services").distinct().order_by("-created_at", "-id")
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="pay-cash")
    def pay_cash(self, request, pk=None):
        request_serializer = self.get_serializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                invoice = get_object_or_404(
                    self.filter_queryset(self.get_queryset()).select_for_update(),
                    pk=pk,
                )
                if invoice.status == Invoice.PAID or invoice.payments.filter(
                    status=Payment.COMPLETED
                ).exists():
                    raise ValidationError({"status": "This invoice has already been paid."})
                if invoice.payments.filter(status=Payment.PENDING).exists():
                    raise ValidationError(
                        {"status": "A payment is already pending for this invoice."}
                    )
                if (
                    invoice.status != Invoice.ISSUED
                    or invoice.total_amount < Decimal("0.01")
                    or invoice.paid_amount != 0
                    or invoice.balance != invoice.total_amount
                ):
                    raise ValidationError(
                        {"status": "Only valid, unpaid issued invoices can be paid."}
                    )

                payment = Payment.objects.create(
                    invoice=invoice,
                    amount=invoice.balance,
                    method=Payment.CASH,
                    status=Payment.COMPLETED,
                    paid_at=timezone.now(),
                    received_by=getattr(request.user, "clinic_profile", None),
                )
                ActiveInvoicePayment.objects.create(
                    invoice=invoice,
                    payment=payment,
                )
                invoice.paid_amount = payment.amount
                invoice.status = Invoice.PAID
                invoice.save(update_fields=["paid_amount", "status"])
        except IntegrityError as error:
            if Payment.objects.filter(
                invoice_id=pk,
                status=Payment.COMPLETED,
            ).exists():
                raise ValidationError(
                    {"status": "This invoice already has a completed payment."}
                ) from error
            logger.exception("Cash payment integrity error for invoice %s", pk)
            return Response(
                {"detail": "The cash payment could not be saved. No changes were applied."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except DatabaseError:
            logger.exception("Cash payment could not be saved for invoice %s", pk)
            return Response(
                {"detail": "The cash payment could not be saved. No changes were applied."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        invoice = self.get_queryset().get(pk=invoice.pk)
        serializer = InvoiceSerializer(
            invoice,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="pay-qr")
    def pay_qr(self, request, pk=None):
        if request.data:
            raise ValidationError({"detail": "QR payment details are generated by the server."})

        try:
            with transaction.atomic():
                invoice = get_object_or_404(
                    self.filter_queryset(self.get_queryset()).select_for_update(),
                    pk=pk,
                )
                if invoice.status == Invoice.PAID or invoice.payments.filter(
                    status=Payment.COMPLETED
                ).exists():
                    raise ValidationError({"status": "This invoice has already been paid."})
                if (
                    invoice.status != Invoice.ISSUED
                    or invoice.total_amount < Decimal("1")
                    or invoice.paid_amount != 0
                    or invoice.balance != invoice.total_amount
                ):
                    raise ValidationError(
                        {"status": "Only valid, unpaid issued invoices can use QR payment."}
                    )

                amount = invoice.balance
                if amount != amount.to_integral_value():
                    raise ValidationError(
                        {"amount": "VietQR requires the invoice amount to be a whole number of VND."}
                    )

                payment = invoice.payments.filter(
                    method=Payment.BANK_TRANSFER,
                    status=Payment.PENDING,
                ).first()
                reused = payment is not None
                if not payment:
                    if invoice.payments.filter(status=Payment.PENDING).exists():
                        raise ValidationError(
                            {"status": "Another payment is already pending for this invoice."}
                        )
                    bank_id = settings.VIETQR_BANK_ID
                    account_number = settings.VIETQR_ACCOUNT_NUMBER
                    account_name = settings.VIETQR_ACCOUNT_NAME
                    if (
                        not re.fullmatch(r"[A-Z0-9]{2,20}", bank_id)
                        or not re.fullmatch(r"\d{4,25}", account_number)
                        or not account_name
                        or len(account_name) > 100
                    ):
                        return Response(
                            {"detail": "VietQR is not configured. Contact an administrator."},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE,
                        )
                    payment = Payment.objects.create(
                        invoice=invoice,
                        amount=amount,
                        method=Payment.BANK_TRANSFER,
                        status=Payment.PENDING,
                        bank_id=bank_id,
                        bank_account_number=account_number,
                        bank_account_name=account_name,
                    )
                    ActiveInvoicePayment.objects.create(
                        invoice=invoice,
                        payment=payment,
                    )
        except IntegrityError as error:
            if Payment.objects.filter(
                invoice_id=pk,
                method=Payment.BANK_TRANSFER,
                status=Payment.PENDING,
            ).exists():
                payment = Payment.objects.get(
                    invoice_id=pk,
                    method=Payment.BANK_TRANSFER,
                    status=Payment.PENDING,
                )
                invoice = self.get_queryset().get(pk=pk)
                reused = True
            else:
                logger.exception("QR payment could not be created for invoice %s", pk)
                return Response(
                    {"detail": "The QR payment could not be created. No changes were applied."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        except DatabaseError:
            logger.exception("QR payment could not be created for invoice %s", pk)
            return Response(
                {"detail": "The QR payment could not be created. No changes were applied."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not payment.bank_id or not payment.bank_account_number or not payment.bank_account_name:
            return Response(
            {"detail": "The pending QR payment is missing its original transfer details. Contact an administrator."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        query = urlencode(
            {
            "amount": f"{payment.amount:.0f}",
            "addInfo": invoice.invoice_number,
            "accountName": payment.bank_account_name,
            }
        )
        transfer = {
            "bank_id": payment.bank_id,
            "account_number": payment.bank_account_number,
            "account_name": payment.bank_account_name,
            "amount": str(payment.amount),
            "description": invoice.invoice_number,
            "status": payment.status,
            "qr_url": (
            f"https://img.vietqr.io/image/{quote(payment.bank_id, safe='')}-"
            f"{quote(payment.bank_account_number, safe='')}-compact2.png?{query}"
            ),
        }
        invoice = self.get_queryset().get(pk=invoice.pk)
        serialized_invoice = InvoiceSerializer(
            invoice,
            context=self.get_serializer_context(),
        ).data
        return Response(
            {"invoice": serialized_invoice, "transfer": transfer, "reused": reused},
            status=status.HTTP_200_OK if reused else status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="reconcile-qr")
    def reconcile_qr(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bank_reference = serializer.validated_data["bank_reference"]
        verified_amount = serializer.validated_data["verified_amount"]

        try:
            with transaction.atomic():
                invoice = get_object_or_404(
                    self.filter_queryset(self.get_queryset()).select_for_update(),
                    pk=pk,
                )
                if invoice.status != Invoice.ISSUED or invoice.paid_amount != 0:
                    raise ValidationError(
                        {"status": "Only unpaid issued invoices can be reconciled."}
                    )
                payment = get_object_or_404(
                    Payment.objects.select_for_update(),
                    invoice=invoice,
                    method=Payment.BANK_TRANSFER,
                    status=Payment.PENDING,
                )
                if payment.amount != invoice.balance or verified_amount != payment.amount:
                    raise ValidationError(
                        {"verified_amount": "The verified bank amount must exactly match the pending invoice transfer."}
                    )
                if BankTransferVerification.objects.filter(reference=bank_reference).exists():
                    raise ValidationError(
                        {"bank_reference": "This bank transaction reference has already been recorded."}
                    )

                BankTransferVerification.objects.create(
                    payment=payment,
                    reference=bank_reference,
                    verified_by=request.user,
                )
                payment.status = Payment.COMPLETED
                payment.paid_at = timezone.now()
                payment.save(
                    update_fields=[
                        "status",
                        "paid_at",
                    ]
                )
                invoice.paid_amount = payment.amount
                invoice.status = Invoice.PAID
                invoice.save(update_fields=["paid_amount", "status"])
        except IntegrityError as error:
            if BankTransferVerification.objects.filter(reference=bank_reference).exists():
                raise ValidationError(
                    {"bank_reference": "This bank transaction reference has already been recorded."}
                ) from error
            logger.exception("QR reconciliation could not be saved for invoice %s", pk)
            return Response(
                {"detail": "The transfer reconciliation could not be saved. No changes were applied."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except DatabaseError:
            logger.exception("QR reconciliation could not be saved for invoice %s", pk)
            return Response(
                {"detail": "The transfer reconciliation could not be saved. No changes were applied."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        invoice = self.get_queryset().get(pk=invoice.pk)
        response_serializer = InvoiceSerializer(
            invoice,
            context=self.get_serializer_context(),
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="cancel-qr")
    def cancel_qr(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                invoice = get_object_or_404(
                    self.filter_queryset(self.get_queryset()).select_for_update(),
                    pk=pk,
                )
                if invoice.status != Invoice.ISSUED or invoice.paid_amount != 0:
                    raise ValidationError(
                        {"status": "Only unpaid issued invoices can cancel a pending transfer."}
                    )
                payment = get_object_or_404(
                    Payment.objects.select_for_update(),
                    invoice=invoice,
                    method=Payment.BANK_TRANSFER,
                    status=Payment.PENDING,
                )
                payment.status = Payment.CANCELLED
                payment.cancelled_at = timezone.now()
                payment.cancelled_by = request.user
                payment.save(
                    update_fields=["status", "cancelled_at", "cancelled_by"]
                )
                ActiveInvoicePayment.objects.filter(
                    invoice=invoice,
                    payment=payment,
                ).delete()
        except DatabaseError:
            logger.exception("Pending QR payment could not be cancelled for invoice %s", pk)
            return Response(
                {"detail": "The pending transfer could not be cancelled. No changes were applied."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        invoice = self.get_queryset().get(pk=invoice.pk)
        response_serializer = InvoiceSerializer(
            invoice,
            context=self.get_serializer_context(),
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return JsonResponse({"status": "ok"})