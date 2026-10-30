import logging
import re
import unicodedata
from collections.abc import Mapping
from datetime import date, datetime, time, timedelta

from django.db import DatabaseError
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.response import Response
from rest_framework.views import APIView

from clinic.models import Doctor, Service, WorkSchedule
from .models import Appointment
from .ai_services import (
    AIServiceConfigurationError,
    AIServiceCredentialsError,
    AIServiceError,
    AIServiceOutputError,
    AIServiceTimeoutError,
    AIServiceUnavailableError,
    generate_project_consultation_answer,
    generate_service_explanation,
)

logger = logging.getLogger(__name__)
SERVICE_ALIASES = {
    "CONSULT": ("tu van", "kiem tra rang"),
    "CLEANING": ("lay cao rang", "ve sinh rang", "danh bong"),
    "FILLING": ("tram rang",),
    "EXTRACTION": ("nho rang",),
    "XRAY": ("chup x quang", "x quang", "chup x-quang", "x-quang", "xray"),
}
EXPLANATION_DISCLAIMER = (
    "Thông tin chỉ mang tính tham khảo, không thay thế tư vấn hoặc chẩn đoán "
    "của bác sĩ."
)
MAX_CHAT_QUESTION_LENGTH = 4000
PROJECT_CONSULTATION_PATTERN = re.compile(
    r"\b(phan tich (bai toan|yeu cau)|"
    r"yeu cau phan mem|"
    r"thiet ke (co so du lieu|database|prompt|kien truc|he thong)|"
    r"khoa chinh|khoa ngoai|"
    r"luong du lieu|"
    r"frontend|backend|"
    r"use case|actor|"
    r"gioi han cua ai|"
    r"prompt|kien truc|"
    r"co so du lieu|"
    r"mo hinh du lieu)\b"
)
PROJECT_CONSULTATION_PERSONAL_DATA_PATTERN = re.compile(
    r"(?<![\w.+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![\w.+-])|"
    r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)|"
    r"\b(so dien thoai|sdt|cccd|cmnd|ten benh nhan|ho ten benh nhan)\b"
)


class ChatQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(
        max_length=MAX_CHAT_QUESTION_LENGTH,
        allow_blank=False,
        trim_whitespace=True,
    )

    def to_internal_value(self, data):
        if isinstance(data, Mapping) and set(data) != {"question"}:
            raise serializers.ValidationError(
                {"detail": "Send only a question. Patient and appointment information is not needed."}
            )
        return super().to_internal_value(data)


def _normalize(value):
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(character for character in value if not unicodedata.combining(character))
    return re.sub(r"\s+", " ", value.replace("đ", "d")).strip()


def _doctor_name(doctor):
    user = doctor.clinic_user.user
    return user.get_full_name().strip() or user.username


def _find_service(question, services):
    normalized_question = _normalize(question)
    matches = []
    for service in services:
        terms = (
            _normalize(service.name),
            _normalize(service.code),
            *(map(_normalize, SERVICE_ALIASES.get(service.code, ()))),
        )
        matching_terms = [
            term for term in terms if term and term in normalized_question
        ]
        if matching_terms:
            matches.append((service, max(matching_terms, key=len)))
    return max(matches, key=lambda match: len(match[1]), default=(None, None))[0]


def _explanation_error_response(code, detail, response_status, retryable=False):
    return Response(
        {"code": code, "detail": detail, "retryable": retryable},
        status=response_status,
    )


def _service_explanation_answer(service):
    if not service.description.strip():
        return (
            "Danh mục chưa có mô tả cho dịch vụ này nên mình chưa thể giải thích "
            "chính xác. Bạn vui lòng liên hệ lễ tân để được hỗ trợ."
        )
    return generate_service_explanation(service)


def _parse_requested_date(question):
    normalized_question = _normalize(question)
    today = timezone.localdate()
    if re.search(r"\b(hom nay|today)\b", normalized_question):
        return today
    if re.search(r"\b(ngay mai|tomorrow)\b", normalized_question):
        return today + timedelta(days=1)

    iso_match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", normalized_question)
    if iso_match:
        try:
            return date.fromisoformat(iso_match.group(1))
        except ValueError:
            return None
    local_match = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](20\d{2})\b", normalized_question)
    if local_match:
        day, month, year = (int(part) for part in local_match.groups())
        try:
            return date(year, month, day)
        except ValueError:
            return None
    local_match_without_year = re.search(r"\b(\d{1,2})[/-](\d{1,2})\b", normalized_question)
    if local_match_without_year:
        day, month = (int(part) for part in local_match_without_year.groups())
        try:
            return date(today.year, month, day)
        except ValueError:
            return None
    return None


def _format_price(service):
    amount = f"{service.price:,.2f}".rstrip("0").rstrip(".")
    return f"{amount} ₫"


def _price_answer(question, services):
    service = _find_service(question, services)
    if service:
        return (
            f"Giá dịch vụ {service.name} hiện là {_format_price(service)} "
            "theo danh mục dịch vụ đang hoạt động. Lễ tân có thể xác nhận giá trước khi khám."
        )
    if not services:
        return "Hiện danh mục chưa có dịch vụ đang hoạt động. Bạn vui lòng liên hệ lễ tân để được hỗ trợ."

    listing = "; ".join(
        f"{service.name}: {_format_price(service)}" for service in services[:10]
    )
    suffix = " Bạn hãy cho biết tên dịch vụ cần hỏi." if len(services) > 10 else ""
    return f"Giá trong danh mục dịch vụ đang hoạt động: {listing}.{suffix}"


def _matching_doctors(question, doctors):
    normalized_question = _normalize(question)
    matches = []
    for doctor in doctors:
        names = [_doctor_name(doctor), doctor.clinic_user.user.username]
        if any(_normalize(name) in normalized_question for name in names if name):
            matches.append(doctor)
    return matches


def _has_unmatched_doctor_name(question, service):
    text = _normalize(question).replace(_normalize(service.name), " ")
    text = re.sub(r"\b20\d{2}-\d{2}-\d{2}\b", " ", text)
    text = re.sub(r"\b\d{1,2}[/-]\d{1,2}[/-]20\d{2}\b", " ", text)
    text = re.sub(
        r"\b(hom nay|ngay mai|today|tomorrow|lich|bac si|doctor|dr|ngay|cho|toi|"
        r"xem|con|gio|nao|kham|dich vu|service|available|free|slot|co|khong)\b",
        " ",
        text,
    )
    return any(token.isalpha() for token in text.split())


def _available_starts(shift, appointments, duration_minutes, requested_date):
    shift_start = datetime.combine(requested_date, shift.start_time)
    shift_end = datetime.combine(requested_date, shift.end_time)
    duration = timedelta(minutes=duration_minutes)
    now = timezone.localtime()
    starts = []

    while shift_start + duration <= shift_end:
        slot_end = shift_start + duration
        aware_start = timezone.make_aware(shift_start, timezone.get_current_timezone())
        aware_end = timezone.make_aware(slot_end, timezone.get_current_timezone())
        if requested_date != now.date() or aware_start > now:
            overlaps = any(
                aware_start < appointment.appointment_date + timedelta(
                    minutes=appointment.service.duration_minutes if appointment.service_id else 30
                )
                and appointment.appointment_date < aware_end
                for appointment in appointments
            )
            if not overlaps:
                starts.append(shift_start.strftime("%H:%M"))
        shift_start += timedelta(minutes=15)
    return starts


def _availability_answer(question, services):
    requested_date = _parse_requested_date(question)
    if requested_date is None:
        return (
            "Để tra giờ còn trống, bạn cho biết ngày muốn khám (ví dụ 25/10/2026) "
            "và tên dịch vụ để hệ thống dùng đúng thời lượng."
        )
    if requested_date < timezone.localdate():
        return "Ngày bạn hỏi đã qua. Bạn hãy cho biết một ngày sắp tới hoặc liên hệ lễ tân."

    service = _find_service(question, services)
    if service is None:
        return (
            "Mình cần tên dịch vụ để tính khoảng thời gian khám chính xác. "
            "Bạn có thể hỏi giá để xem danh mục dịch vụ hoặc liên hệ lễ tân."
        )

    doctors = list(
        Doctor.objects.select_related("clinic_user__user", "clinic_user__role").order_by(
            "clinic_user__user__first_name",
            "clinic_user__user__last_name",
            "id",
        )
    )
    requested_doctors = _matching_doctors(question, doctors)
    if not requested_doctors and _has_unmatched_doctor_name(question, service):
        return (
            "Mình chưa tìm thấy bác sĩ được nêu trong câu hỏi. "
            "Bạn hãy kiểm tra tên bác sĩ hoặc liên hệ lễ tân."
        )
    if not requested_doctors:
        requested_doctors = doctors

    schedules = WorkSchedule.objects.filter(
        doctor__in=requested_doctors,
        work_date=requested_date,
    ).select_related("doctor__clinic_user__user")
    day_start = timezone.make_aware(
        datetime.combine(requested_date, time.min),
        timezone.get_current_timezone(),
    )
    day_end = day_start + timedelta(days=1)
    appointment_rows = Appointment.objects.filter(
        doctor__in=requested_doctors,
        appointment_date__gte=day_start,
        appointment_date__lt=day_end,
    ).exclude(status=Appointment.Status.CANCELLED).select_related("service")
    appointments_by_doctor = {}
    for appointment in appointment_rows:
        appointments_by_doctor.setdefault(appointment.doctor_id, []).append(appointment)

    available_by_doctor = []
    for doctor in requested_doctors:
        doctor_shifts = [shift for shift in schedules if shift.doctor_id == doctor.id]
        doctor_appointments = appointments_by_doctor.get(doctor.id, [])
        available = []
        for shift in doctor_shifts:
            available.extend(
                _available_starts(shift, doctor_appointments, service.duration_minutes, requested_date)
            )
        if available:
            available_by_doctor.append((_doctor_name(doctor), sorted(set(available))))

    if not available_by_doctor:
        return (
            f"Mình không tìm thấy khung giờ trống theo ca làm và lịch hẹn hiện có "
            f"cho dịch vụ {service.name} ngày {requested_date.strftime('%d/%m/%Y')}. "
            "Lịch có thể thay đổi; vui lòng liên hệ lễ tân để kiểm tra lại."
        )

    entries = []
    for doctor_name, starts in available_by_doctor[:8]:
        shown_starts = starts[:8]
        suffix = " (còn các giờ khác)" if len(starts) > len(shown_starts) else ""
        entries.append(f"{doctor_name}: {', '.join(shown_starts)}{suffix}")
    omitted_doctors = len(available_by_doctor) > len(entries)
    return (
        f"Khung giờ bắt đầu còn trống theo dữ liệu hiện có cho {service.name} "
        f"ngày {requested_date.strftime('%d/%m/%Y')} (thời lượng {service.duration_minutes} phút; "
        "các giờ gợi ý cách nhau 15 phút): "
        + "; ".join(entries)
        + ("; còn bác sĩ khác có giờ phù hợp." if omitted_doctors else ".")
        + " Đây chưa phải xác nhận đặt lịch; vui lòng liên hệ lễ tân để giữ giờ."
    )


class ChatbotAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "ai_chat"

    def post(self, request):
        serializer = ChatQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data["question"]
        normalized_question = _normalize(question)

        if re.search(
            r"\b(cap cuu|kho tho|sung mat|mat dang sung|chay mau nhieu|"
            r"dau du doi|dau rat nhieu)\b",
            normalized_question,
        ):
            answer = (
                "Chatbot không tư vấn y tế hoặc xử lý tình huống khẩn cấp. "
                "Bạn hãy liên hệ ngay cơ sở y tế hoặc lễ tân để được hướng dẫn trực tiếp."
            )
            return Response({"answer": answer, "intent": "handoff"})

        is_project_consultation = bool(
            PROJECT_CONSULTATION_PATTERN.search(normalized_question)
        )
        if (
            is_project_consultation
            and PROJECT_CONSULTATION_PERSONAL_DATA_PATTERN.search(question)
        ):
            return Response(
                {
                    "answer": (
                        "Để bảo vệ quyền riêng tư, vui lòng xóa tên, số điện thoại, email "
                        "hoặc thông tin hồ sơ bệnh nhân khỏi câu hỏi rồi gửi lại."
                    ),
                    "intent": "privacy_guard",
                }
            )

        try:
            services = list(
                Service.objects.filter(is_active=True).order_by("name", "id")
            )
            is_availability = bool(
                re.search(
                    r"\b(lich|ranh|khung gio|gio nao|bac si|doctor|appointment|available|free|slot)\b",
                    normalized_question,
                )
            )
            is_price = bool(
                re.search(
                    r"\b(gia|bao nhieu|tien|phi|bang gia|cost|price)\b",
                    normalized_question,
                )
            )
            is_explanation = bool(
                re.search(
                    r"\b(giai thich|la gi|la nhu the nao|cong dung|dung de lam gi|"
                    r"what is|explain|"
                    r"how does it work)\b",
                    normalized_question,
                )
            )
            if is_project_consultation:
                answer = generate_project_consultation_answer(question)
                intent = "project_consultation"
            elif is_availability:
                answer = _availability_answer(question, services)
                intent = "availability"
            elif is_price:
                answer = _price_answer(question, services)
                intent = "price"
            elif is_explanation:
                service = _find_service(question, services)
                if service is None:
                    answer = (
                        "Bạn hãy cho biết tên dịch vụ cần giải thích, ví dụ "
                        "“giải thích dịch vụ trám răng”."
                    )
                    intent = "service_explanation"
                else:
                    answer = _service_explanation_answer(service)
                    intent = "service_explanation"
            else:
                answer = (
                    "Mình có thể hỗ trợ tra giá dịch vụ, giờ khám còn trống, giải thích dịch vụ "
                    "hoặc trả lời câu hỏi học tập về phân tích yêu cầu, cơ sở dữ liệu, kiến trúc "
                    "và prompt AI của đề tài. Mình không chẩn đoán, tư vấn điều trị, xem hồ sơ "
                    "bệnh nhân hay đặt lịch qua chat. Nếu cần hỗ trợ khác, vui lòng liên hệ lễ tân."
                )
                intent = "out_of_scope"
        except DatabaseError:
            logger.warning("Chatbot could not read service or schedule data.")
            return Response(
                {
                    "answer": "Hiện chưa thể đọc dữ liệu giá/lịch khám. Vui lòng thử lại sau hoặc liên hệ lễ tân.",
                    "intent": "unavailable",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except AIServiceCredentialsError:
            logger.error("Gemini rejected the configured API credentials.")
            return _explanation_error_response(
                "ai_credentials_invalid",
                "Gemini từ chối khóa API. Hãy thu hồi khóa đã lộ, tạo khóa mới và cấu hình lại trong tiến trình backend.",
                status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except AIServiceConfigurationError:
            logger.error("Gemini configuration is missing or was rejected.")
            return _explanation_error_response(
                "ai_configuration_invalid",
                "Cấu hình AI chưa hợp lệ. Kiểm tra tên model và khóa Gemini trong tiến trình backend.",
                status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except AIServiceTimeoutError:
            logger.warning("Gemini chatbot request timed out.")
            return _explanation_error_response(
                "ai_timeout",
                "AI phản hồi quá thời gian chờ. Vui lòng thử lại.",
                status.HTTP_504_GATEWAY_TIMEOUT,
                retryable=True,
            )
        except AIServiceUnavailableError as error:
            logger.warning("Gemini chatbot is temporarily unavailable: %s", error)
            rate_limited = "HTTP 429" in str(error)
            return _explanation_error_response(
                "ai_rate_limited" if rate_limited else "ai_unavailable",
                (
                    "Gemini đang giới hạn yêu cầu hoặc quota đã hết. Kiểm tra quota và giới hạn "
                    "của dự án trong Google AI Studio rồi thử lại."
                    if rate_limited
                    else "Gemini chưa phản hồi. Kiểm tra kết nối Internet của backend và trạng thái dịch vụ, rồi thử lại."
                ),
                status.HTTP_503_SERVICE_UNAVAILABLE,
                retryable=True,
            )
        except AIServiceOutputError as error:
            logger.warning("Gemini chatbot returned invalid output: %s", error)
            return _explanation_error_response(
                "ai_generation_failed",
                "AI chưa trả về câu trả lời hoàn chỉnh. Vui lòng thử lại.",
                status.HTTP_502_BAD_GATEWAY,
                retryable=True,
            )
        except AIServiceError:
            logger.warning("Gemini chatbot request failed.")
            return _explanation_error_response(
                "ai_generation_failed",
                "Không thể tạo giải thích do phản hồi không hợp lệ từ dịch vụ AI.",
                status.HTTP_502_BAD_GATEWAY,
            )

        return Response({"answer": answer, "intent": intent}, status=status.HTTP_200_OK)
