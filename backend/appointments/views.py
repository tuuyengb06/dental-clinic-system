import logging

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.exceptions import Throttled, ValidationError
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
    AIServiceOutputError,
    AIServiceTimeoutError,
    AIServiceUnavailableError,
    generate_generic_follow_up_text,
    generate_medical_record_summary,
)
from .sms_services import SMSServiceError, build_follow_up_message

logger = logging.getLogger(__name__)


def _ai_error_response(code, detail, response_status, retryable=False, errors=None):
    payload = {
        "code": code,
        "detail": detail,
        "retryable": retryable,
    }
    if errors is not None:
        payload["errors"] = errors
    return Response(payload, status=response_status)


class IsAppointmentStaff(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        clinic_profile = getattr(request.user, "clinic_profile", None)
        clinic_role = clinic_profile.role.code if clinic_profile else None
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return bool(
                request.user.is_superuser
                or clinic_role in ("ADMIN", "DENTIST", "RECEPTIONIST")
                or getattr(request.user, "patient_profile", None)
            )
        if (
            getattr(view, "allow_patient_booking", False)
            and getattr(view, "action", None) == "create"
            and request.method == "POST"
        ):
            return bool(
                request.user.is_superuser
                or clinic_role in ("ADMIN", "RECEPTIONIST")
                or getattr(request.user, "patient_profile", None)
            )
        return bool(request.user.is_superuser or clinic_role in ("ADMIN", "RECEPTIONIST"))


class IsDentistOrAdmin(BasePermission):
    def has_permission(self, request, view):
        clinic_profile = getattr(request.user, "clinic_profile", None)
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser or (
            clinic_profile and clinic_profile.role.code in ("ADMIN", "DENTIST")
        ):
            return True
        return bool(
            request.method in ("GET", "HEAD", "OPTIONS")
            and getattr(request.user, "patient_profile", None)
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
            return bool(
                request.user.is_superuser
                or getattr(request.user, "patient_profile", None)
                or (
                    getattr(request.user, "clinic_profile", None)
                    and request.user.clinic_profile.role.code
                    in ("ADMIN", "DENTIST", "RECEPTIONIST")
                )
            )
        clinic_profile = getattr(request.user, "clinic_profile", None)
        return bool(
            request.user.is_superuser
            or (clinic_profile and clinic_profile.role.code in ("ADMIN", "RECEPTIONIST"))
        )


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAppointmentStaff]
    allow_patient_booking = True

    def get_queryset(self):
        queryset = Appointment.objects.select_related(
            "patient", "doctor__clinic_user__user", "service"
        )
        clinic_profile = getattr(self.request.user, "clinic_profile", None)
        if clinic_profile and clinic_profile.role.code == "DENTIST":
            return queryset.filter(doctor__clinic_user=clinic_profile)
        patient = getattr(self.request.user, "patient_profile", None)
        if patient:
            return queryset.filter(patient=patient)
        if not self.request.user.is_superuser and not clinic_profile:
            return queryset.none()
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
        patient = getattr(self.request.user, "patient_profile", None)
        if patient:
            return queryset.filter(appointment__patient=patient)
        if not self.request.user.is_superuser and not clinic_profile:
            return queryset.none()
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
            return _ai_error_response(
                "invalid_input",
                "API tóm tắt không nhận dữ liệu đầu vào. Hãy lưu hồ sơ rồi thử lại.",
                status.HTTP_400_BAD_REQUEST,
            )
        record = self.get_object()
        if not record.appointment.patient.ai_processing_consent:
            return _ai_error_response(
                "invalid_input",
                "Cần ghi nhận sự đồng ý xử lý AI của bệnh nhân trước khi tạo tóm tắt.",
                status.HTTP_400_BAD_REQUEST,
            )
        try:
            summary = generate_medical_record_summary(record)
        except AIServiceConfigurationError as error:
            logger.error("Gemini medical-record summary is not configured: %s", error)
            return _ai_error_response(
                "ai_unavailable",
                "Dịch vụ AI chưa được cấu hình. Vui lòng liên hệ quản trị viên.",
                status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except AIServiceTimeoutError:
            logger.warning("Gemini medical-record summary request timed out.")
            return _ai_error_response(
                "ai_timeout",
                "AI phản hồi quá thời gian chờ. Vui lòng thử lại.",
                status.HTTP_504_GATEWAY_TIMEOUT,
                retryable=True,
            )
        except AIServiceUnavailableError:
            logger.warning("Gemini medical-record summary is temporarily unavailable.")
            return _ai_error_response(
                "ai_unavailable",
                "Dịch vụ AI đang tạm thời không khả dụng sau số lần thử tối đa. Vui lòng thử lại sau.",
                status.HTTP_503_SERVICE_UNAVAILABLE,
                retryable=True,
            )
        except AIServiceOutputError as error:
            logger.warning("Gemini medical-record summary returned invalid output: %s", error)
            return _ai_error_response(
                "ai_generation_failed",
                "AI trả về nội dung không hợp lệ. Vui lòng thử lại.",
                status.HTTP_502_BAD_GATEWAY,
                retryable=True,
            )
        except AIServiceError as error:
            logger.warning("Gemini medical-record summary request failed: %s", error)
            return _ai_error_response(
                "ai_generation_failed",
                "Không thể tạo tóm tắt AI do phản hồi không hợp lệ từ dịch vụ.",
                status.HTTP_502_BAD_GATEWAY,
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
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "ai_reminder_preview"

    def handle_exception(self, exc):
        if isinstance(exc, Throttled):
            response = _ai_error_response(
                "rate_limited",
                "Đã đạt giới hạn tạo bản nháp AI. Vui lòng chờ rồi thử lại.",
                status.HTTP_429_TOO_MANY_REQUESTS,
                retryable=True,
            )
            if exc.wait is not None:
                response["Retry-After"] = str(max(1, round(exc.wait)))
            return response
        return super().handle_exception(exc)

    def post(self, request):
        serializer = FollowUpReminderRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return _ai_error_response(
                "invalid_input",
                "Dữ liệu đầu vào không hợp lệ. Vui lòng kiểm tra hồ sơ được chọn.",
                status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors,
            )
        record = MedicalRecord.objects.select_related(
            "appointment__patient"
        ).filter(
            pk=serializer.validated_data["medical_record_id"]
        ).exclude(
            appointment__status=Appointment.Status.CANCELLED
        ).first()
        if record is None:
            return _ai_error_response(
                "record_not_found",
                "Không tìm thấy lịch tái khám đã chọn.",
                status.HTTP_404_NOT_FOUND,
            )
        if record.follow_up_date is None:
            return _ai_error_response(
                "invalid_input",
                "Hồ sơ chưa có ngày tái khám. Vui lòng kiểm tra dữ liệu hồ sơ.",
                status.HTTP_400_BAD_REQUEST,
            )
        if not record.appointment.patient.sms_reminder_consent:
            return _ai_error_response(
                "invalid_input",
                "Chưa ghi nhận SMS consent. Vui lòng xác nhận consent trước khi tạo bản nháp.",
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            generic_text = generate_generic_follow_up_text()
            message = build_follow_up_message(record.follow_up_date, generic_text)
        except AIServiceConfigurationError as error:
            logger.error("Gemini follow-up reminder is not configured: %s", error)
            return _ai_error_response(
                "ai_unavailable",
                "Dịch vụ AI chưa được cấu hình. Vui lòng liên hệ quản trị viên.",
                status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except AIServiceTimeoutError:
            logger.warning("Gemini follow-up reminder request timed out.")
            return _ai_error_response(
                "ai_timeout",
                "AI phản hồi quá thời gian chờ. Vui lòng thử lại.",
                status.HTTP_504_GATEWAY_TIMEOUT,
                retryable=True,
            )
        except AIServiceUnavailableError:
            logger.warning("Gemini follow-up reminder is temporarily unavailable.")
            return _ai_error_response(
                "ai_unavailable",
                "Dịch vụ AI đang tạm thời không khả dụng sau số lần thử tối đa. Vui lòng thử lại sau.",
                status.HTTP_503_SERVICE_UNAVAILABLE,
                retryable=True,
            )
        except AIServiceOutputError as error:
            logger.warning("Gemini follow-up reminder returned invalid output: %s", error)
            return _ai_error_response(
                "ai_generation_failed",
                "AI trả về nội dung không hợp lệ. Vui lòng thử lại.",
                status.HTTP_502_BAD_GATEWAY,
                retryable=True,
            )
        except (AIServiceError, SMSServiceError) as error:
            logger.warning("AI follow-up reminder preview could not be generated: %s", error)
            return _ai_error_response(
                "ai_generation_failed",
                "Không thể tạo bản nháp do phản hồi không hợp lệ từ dịch vụ AI.",
                status.HTTP_502_BAD_GATEWAY,
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