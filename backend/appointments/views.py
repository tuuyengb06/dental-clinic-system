import logging

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import Appointment, MedicalRecord
from .serializers import (
    AppointmentSerializer,
    FollowUpAppointmentSerializer,
    FollowUpReminderRequestSerializer,
    MedicalRecordSerializer,
)
from .ai_services import (
    AIServiceConfigurationError,
    AIServiceError,
    generate_generic_follow_up_text,
    generate_medical_record_summary,
)
from .sms_services import SMSServiceError, build_follow_up_message

logger = logging.getLogger(__name__)


class IsAppointmentStaff(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        clinic_profile = getattr(request.user, "clinic_profile", None)
        return bool(
            request.user.is_superuser
            or (clinic_profile and clinic_profile.role.code in ("ADMIN", "RECEPTIONIST"))
        )


class IsDentistOrAdmin(BasePermission):
    def has_permission(self, request, view):
        clinic_profile = getattr(request.user, "clinic_profile", None)
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_superuser
                or (
                    clinic_profile
                    and clinic_profile.role.code in ("ADMIN", "DENTIST")
                )
            )
        )


class IsReceptionistOrAdmin(BasePermission):
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


class IsScheduleStaff(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        clinic_profile = getattr(request.user, "clinic_profile", None)
        return bool(
            request.user.is_superuser
            or (clinic_profile and clinic_profile.role.code in ("ADMIN", "RECEPTIONIST"))
        )


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAppointmentStaff]

    def get_queryset(self):
        queryset = Appointment.objects.select_related(
            "patient", "doctor__clinic_user__user", "service"
        )
        clinic_profile = getattr(self.request.user, "clinic_profile", None)
        if clinic_profile and clinic_profile.role.code == "DENTIST":
            return queryset.filter(doctor__clinic_user=clinic_profile)
        return queryset

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        with transaction.atomic():
            appointment = self.get_object()
            if appointment.status == Appointment.Status.CANCELLED:
                raise ValidationError({"status": "This appointment is already cancelled."})
            if appointment.status not in (
                Appointment.Status.PENDING,
                Appointment.Status.CONFIRMED,
            ):
                raise ValidationError(
                    {"status": "Only pending or confirmed appointments can be cancelled."}
                )
            appointment.status = Appointment.Status.CANCELLED
            appointment.save(update_fields=["status"])
        return Response(self.get_serializer(appointment).data, status=status.HTTP_200_OK)


class MedicalRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsDentistOrAdmin]

    def get_queryset(self):
        queryset = MedicalRecord.objects.select_related(
            "appointment__patient", "appointment__doctor__clinic_user__user"
        ).prefetch_related("teeth", "services")
        clinic_profile = getattr(self.request.user, "clinic_profile", None)
        if clinic_profile and clinic_profile.role.code == "DENTIST":
            return queryset.filter(appointment__doctor__clinic_user=clinic_profile)
        return queryset

    def get_throttles(self):
        if self.action == "ai_summary":
            self.throttle_scope = "ai_summary"
            return [ScopedRateThrottle()]
        return super().get_throttles()

    @action(
        detail=True,
        methods=["post"],
        url_path="ai-summary",
        throttle_classes=[ScopedRateThrottle],
    )
    def ai_summary(self, request, pk=None):
        if request.data:
            raise ValidationError({"detail": "No request fields are needed for an AI summary."})
        record = self.get_object()
        if not record.appointment.patient.ai_processing_consent:
            raise ValidationError(
                {"consent": "Patient consent for AI processing must be recorded first."}
            )
        try:
            summary = generate_medical_record_summary(record)
        except AIServiceConfigurationError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except AIServiceError as error:
            logger.warning("Gemini medical-record summary request failed: %s", error)
            return Response(
                {"detail": "AI summary could not be generated. Please try again later."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response({"summary": summary, "provider": "Gemini"})


class FollowUpAppointmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FollowUpAppointmentSerializer
    permission_classes = [IsReceptionistOrAdmin]

    def get_queryset(self):
        return (
            MedicalRecord.objects.filter(follow_up_date__isnull=False)
            .exclude(appointment__status=Appointment.Status.CANCELLED)
            .select_related(
                "appointment__patient",
                "appointment__doctor__clinic_user__user",
            )
            .order_by("follow_up_date", "appointment__appointment_date", "id")
        )


class GenerateFollowUpReminderAPIView(APIView):
    permission_classes = [IsReceptionistOrAdmin]

    def post(self, request):
        serializer = FollowUpReminderRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = MedicalRecord.objects.select_related(
            "appointment__patient"
        ).filter(
            pk=serializer.validated_data["medical_record_id"]
        ).exclude(
            appointment__status=Appointment.Status.CANCELLED
        ).first()
        if record is None:
            return Response(
                {"detail": "Follow-up appointment was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if record.follow_up_date is None:
            raise ValidationError(
                {"follow_up_date": "This record has no follow-up date."}
            )
        if not record.appointment.patient.sms_reminder_consent:
            raise ValidationError(
                {"consent": "Patient consent for SMS reminders must be recorded first."}
            )

        try:
            generic_text = generate_generic_follow_up_text()
            message = build_follow_up_message(record.follow_up_date, generic_text)
        except AIServiceConfigurationError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except (AIServiceError, SMSServiceError) as error:
            logger.warning("AI follow-up reminder preview could not be generated: %s", error)
            return Response(
                {"detail": "Reminder preview could not be generated. Please try again later."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                "medical_record_id": record.pk,
                "follow_up_date": record.follow_up_date,
                "message": message,
                "provider": "Gemini",
                "sent": False,
            }
        )