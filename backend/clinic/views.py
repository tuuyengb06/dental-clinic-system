import re

from django.db import IntegrityError
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from appointments.models import MedicalRecord
from .models import Doctor, Patient, Tooth, WorkSchedule, Service, Invoice
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
    PatientSerializer,
    ToothSerializer,
    WorkScheduleSerializer,
)


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
            "items__service"
        ).order_by("-issued_at", "-id")

    def get_serializer_class(self):
        if self.action == "create":
            return InvoiceCreateSerializer
        if self.action == "available_records":
            return InvoiceSourceSerializer
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


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return JsonResponse({"status": "ok"})