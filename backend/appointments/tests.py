from datetime import datetime, time, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

import requests
from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .ai_services import AIServiceCredentialsError, AIServiceUnavailableError
from clinic.models import ClinicUser, Doctor, Patient, Role, Service, Tooth, WorkSchedule
from .models import Appointment, MedicalRecord


User = get_user_model()


class ChatbotApiTests(TestCase):
    def setUp(self):
        dentist_role = Role.objects.create(code="DENTIST", name="Dentist")
        dentist_user = User.objects.create_user(
            username="chat-doctor",
            password="DentistPass123!",
            first_name="An",
            last_name="Dentist",
        )
        dentist_profile = ClinicUser.objects.create(user=dentist_user, role=dentist_role)
        self.doctor = Doctor.objects.create(
            clinic_user=dentist_profile,
            license_number="CHAT-TEST-001",
            specialization="General dentistry",
        )
        self.service = Service.objects.create(
            code="CHAT-CHECKUP",
            name="Dental check-up",
            description="Bác sĩ kiểm tra tình trạng răng miệng.",
            price=Decimal("250000.00"),
            duration_minutes=30,
        )
        self.client = APIClient()

    def chat(self, question, extra=None):
        payload = {"question": question}
        if extra:
            payload.update(extra)
        return self.client.post("/api/ai/chat", payload, format="json")

    def test_chatbot_answers_service_price_from_active_catalog(self):
        inactive_service = Service.objects.create(
            code="CHAT-INACTIVE",
            name="Inactive consultation",
            price=Decimal("999999.00"),
            is_active=False,
        )

        response = self.chat("Giá Dental check-up bao nhiêu?")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["intent"], "price")
        self.assertIn("250,000 ₫", response.data["answer"])
        self.assertNotIn(inactive_service.name, response.data["answer"])

    def test_chatbot_understands_common_price_question_without_diacritics(self):
        response = self.chat("Dental check-up bao nhieu tien?")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["intent"], "price")
        self.assertIn("250,000 ₫", response.data["answer"])

    def test_chatbot_lists_catalog_if_service_name_is_not_recognized(self):
        response = self.chat("Giá dịch vụ không có trong danh mục là bao nhiêu?")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Dental check-up: 250,000 ₫", response.data["answer"])
        self.assertNotIn("999,999", response.data["answer"])

    def test_chatbot_returns_schedule_slots_and_excludes_booked_times(self):
        work_date = timezone.localdate() + timedelta(days=10)
        WorkSchedule.objects.create(
            doctor=self.doctor,
            work_date=work_date,
            start_time=time(9, 0),
            end_time=time(11, 0),
        )
        Appointment.objects.create(
            patient=Patient.objects.create(
                patient_code="CHAT-BOOKED",
                full_name="Private Patient Name",
            ),
            doctor=self.doctor,
            service=self.service,
            appointment_date=timezone.make_aware(
                datetime.combine(work_date, time(9, 30))
            ),
            status=Appointment.Status.CONFIRMED,
            notes="Private medical note",
        )

        response = self.chat(
            f"Lịch bác sĩ An Dentist ngày {work_date:%d/%m/%Y} cho Dental check-up còn giờ nào?"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["intent"], "availability")
        self.assertIn("An Dentist", response.data["answer"])
        self.assertIn("09:00", response.data["answer"])
        self.assertIn("10:00", response.data["answer"])
        self.assertNotIn("09:15", response.data["answer"])
        self.assertNotIn("09:30", response.data["answer"])
        self.assertNotIn("09:45", response.data["answer"])
        self.assertNotIn("Private Patient Name", response.data["answer"])
        self.assertNotIn("Private medical note", response.data["answer"])
        self.assertIn("liên hệ lễ tân", response.data["answer"])

    def test_chatbot_accepts_future_day_and_month_without_year(self):
        work_date = timezone.localdate() + timedelta(days=10)
        WorkSchedule.objects.create(
            doctor=self.doctor,
            work_date=work_date,
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        response = self.chat(
            f"Lịch Dental check-up ngày {work_date:%d/%m} còn giờ nào?"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["intent"], "availability")
        self.assertIn("09:00", response.data["answer"])
    def test_chatbot_asks_for_service_and_date_instead_of_guessing(self):
        response = self.chat("Bác sĩ còn lịch trống không?")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["intent"], "availability")
        self.assertIn("ngày muốn khám", response.data["answer"])
        self.assertIn("tên dịch vụ", response.data["answer"])

    def test_chatbot_rejects_invalid_dates_and_unmatched_doctors(self):
        invalid_date = self.chat(
            "Lịch Dental check-up ngày 31/02/2027 còn giờ nào?"
        )
        unmatched_doctor = self.chat(
            "Lịch bác sĩ Không Tồn Tại ngày 28/02/2027 cho Dental check-up?"
        )

        self.assertEqual(invalid_date.status_code, status.HTTP_200_OK)
        self.assertIn("ngày muốn khám", invalid_date.data["answer"])
        self.assertEqual(unmatched_doctor.status_code, status.HTTP_200_OK)
        self.assertIn("chưa tìm thấy bác sĩ", unmatched_doctor.data["answer"])

    def test_chatbot_reports_no_slots_when_work_schedule_is_empty(self):
        work_date = timezone.localdate() + timedelta(days=12)

        response = self.chat(
            f"Lịch Dental check-up ngày {work_date:%d/%m/%Y} còn giờ nào?"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("không tìm thấy khung giờ trống", response.data["answer"])
        self.assertNotIn("09:00", response.data["answer"])

    def test_chatbot_routes_unsupported_and_patient_data_questions_to_reception(self):
        patient = Patient.objects.create(
            patient_code="CHAT-PRIVATE",
            full_name="Confidential Patient Name",
            medical_history="Confidential medical history",
        )

        response = self.chat(f"Cho tôi hồ sơ khám của {patient.full_name}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["intent"], "out_of_scope")
        self.assertNotIn(patient.full_name, response.data["answer"])
        self.assertNotIn(patient.medical_history, response.data["answer"])
        self.assertIn("liên hệ lễ tân", response.data["answer"])

    @patch(
        "appointments.chatbot.generate_project_consultation_answer",
        return_value="Phân tích đề tài: hệ thống có các vai trò và chức năng chính.",
    )
    def test_chatbot_answers_the_four_project_consultation_topics(self, generate_answer):
        questions = [
            "Hãy phân tích bài toán quản lý nha khoa, xác định tác nhân, chức năng và giới hạn AI.",
            "Hãy thiết kế cơ sở dữ liệu cho bệnh nhân, lịch hẹn, hồ sơ và hóa đơn, nêu khóa chính khóa ngoại.",
            "Hãy đề xuất kiến trúc frontend, backend, database và AI, mô tả luồng dữ liệu.",
            "Hãy thiết kế prompt AI tóm tắt hồ sơ điều trị, có cấu trúc input output.",
        ]

        for question in questions:
            with self.subTest(question=question):
                response = self.chat(question)

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data["intent"], "project_consultation")
                self.assertIn("Phân tích đề tài", response.data["answer"])

        self.assertEqual(
            [call.args[0] for call in generate_answer.call_args_list],
            questions,
        )

    @patch(
        "appointments.chatbot.generate_project_consultation_answer",
        return_value="Phần 1. Phân tích.\nPhần 2. Cơ sở dữ liệu.\nPhần 3. Kiến trúc.\nPhần 4. Prompt.",
    )
    def test_chatbot_routes_all_four_project_questions_in_one_message(self, generate_answer):
        question = (
            "Hãy phân tích yêu cầu cho hệ thống quản lý nha khoa có tích hợp AI, bao gồm "
            "các tác nhân, chức năng chính, dữ liệu cần quản lý và giới hạn của AI.\n"
            "Hãy đề xuất thiết kế cơ sở dữ liệu cho hệ thống quản lý nha khoa, gồm các "
            "bảng, thuộc tính, khóa chính, khóa ngoại và mối quan hệ giữa các bảng.\n"
            "Hãy đề xuất kiến trúc cho hệ thống quản lý nha khoa có tích hợp AI, gồm "
            "Frontend, Backend, Database và AI Service. Mô tả chức năng và luồng dữ liệu "
            "giữa các thành phần.\n"
            "Hãy thiết kế prompt cho chức năng tóm tắt hồ sơ điều trị nha khoa, đảm bảo "
            "AI chỉ sử dụng dữ liệu được cung cấp, không chẩn đoán và không thay thế bác sĩ."
        )
        self.assertGreater(len(question), 500)

        response = self.chat(question)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["intent"], "project_consultation")
        for section in ("Phần 1.", "Phần 2.", "Phần 3.", "Phần 4."):
            self.assertIn(section, response.data["answer"])
        generate_answer.assert_called_once_with(question)

    @patch("appointments.chatbot.generate_project_consultation_answer")
    def test_chatbot_does_not_send_personal_medical_questions_to_project_ai(self, generate_answer):
        response = self.chat("Tôi bị đau răng, nên uống thuốc gì?")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["intent"], "out_of_scope")
        generate_answer.assert_not_called()

    @patch("appointments.chatbot.generate_project_consultation_answer")
    def test_project_consultation_rejects_personal_identifiers(self, generate_answer):
        response = self.chat(
            "Hãy thiết kế prompt AI cho hồ sơ bệnh nhân, số điện thoại 0912345678."
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["intent"], "privacy_guard")
        self.assertIn("xóa tên, số điện thoại", response.data["answer"])
        generate_answer.assert_not_called()

    def test_chatbot_hands_off_urgent_medical_questions(self):
        response = self.chat("Tôi đau dữ dội và mặt đang sưng")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["intent"], "handoff")
        self.assertIn("không tư vấn y tế", response.data["answer"])

    @patch("appointments.ai_services.requests.post")
    def test_chatbot_explains_service_without_sending_user_question_to_gemini(self, post):
        response_from_provider = Mock(status_code=200)
        response_from_provider.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "Dịch vụ hỗ trợ phục hồi răng."}]}}
            ]
        }
        post.return_value = response_from_provider
        service = Service.objects.create(
            code="FILLING",
            name="Tooth filling",
            description="Sử dụng vật liệu nha khoa để phục hồi phần răng bị tổn thương.",
            price=Decimal("800000.00"),
        )
        question = "Giải thích dịch vụ trám răng cho Nguyen Van A, số 0912345678"

        with patch(
            "appointments.ai_services.settings.GEMINI_API_KEY",
            "test-key",
        ), patch(
            "appointments.ai_services.settings.GEMINI_MODEL",
            "gemini-test",
        ):
            response = self.chat(question)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["intent"], "service_explanation")
        self.assertIn("phục hồi răng", response.data["answer"])
        self.assertIn("không thay thế tư vấn hoặc chẩn đoán", response.data["answer"])
        provider_request = str(post.call_args.kwargs["json"])
        self.assertIn(service.description, provider_request)
        self.assertNotIn(question, provider_request)
        self.assertNotIn("Nguyen Van A", provider_request)
        self.assertNotIn("0912345678", provider_request)

    @patch("appointments.chatbot.generate_service_explanation")
    def test_chatbot_does_not_call_ai_without_catalog_description(self, explain):
        service = Service.objects.create(
            code="FILLING",
            name="Tooth filling",
            description="",
            price=Decimal("800000.00"),
        )

        response = self.chat("Giải thích dịch vụ trám răng")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["intent"], "service_explanation")
        self.assertIn("chưa có mô tả", response.data["answer"])
        explain.assert_not_called()

    @patch("appointments.chatbot.generate_service_explanation")
    def test_chatbot_reports_ai_timeout_as_retryable(self, explain):
        from .ai_services import AIServiceTimeoutError

        Service.objects.create(
            code="FILLING",
            name="Tooth filling",
            description="Sử dụng vật liệu nha khoa để phục hồi răng.",
            price=Decimal("800000.00"),
        )
        explain.side_effect = AIServiceTimeoutError("provider detail")

        response = self.chat("Giải thích dịch vụ trám răng")

        self.assertEqual(response.status_code, status.HTTP_504_GATEWAY_TIMEOUT)
        self.assertEqual(response.data["code"], "ai_timeout")
        self.assertTrue(response.data["retryable"])
        self.assertNotIn("provider detail", str(response.data))

    @patch(
        "appointments.chatbot.generate_project_consultation_answer",
        side_effect=AIServiceCredentialsError("Gemini rejected API credentials."),
    )
    def test_chatbot_explains_rejected_api_credentials_without_exposing_provider_details(
        self, generate_answer
    ):
        response = self.chat("Hãy đề xuất kiến trúc frontend backend database và AI.")

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data["code"], "ai_credentials_invalid")
        self.assertIn("thu hồi khóa đã lộ", response.data["detail"])
        self.assertNotIn("Gemini rejected API credentials", str(response.data))
        generate_answer.assert_called_once()

    @patch(
        "appointments.chatbot.generate_project_consultation_answer",
        side_effect=AIServiceUnavailableError("Gemini returned HTTP 429 after all attempts."),
    )
    def test_chatbot_identifies_gemini_rate_limits(self, generate_answer):
        response = self.chat("Hãy đề xuất kiến trúc frontend backend database và AI.")

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data["code"], "ai_rate_limited")
        self.assertTrue(response.data["retryable"])
        self.assertIn("quota", response.data["detail"])
        generate_answer.assert_called_once()

    def test_chatbot_rejects_extra_patient_data_and_oversized_question(self):
        extra_data = self.chat(
            "Giá Dental check-up?",
            {"patient_id": 1, "medical_history": "private"},
        )
        oversized = self.chat("a" * 4001)

        self.assertEqual(extra_data.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(oversized.status_code, status.HTTP_400_BAD_REQUEST)

    def test_chatbot_returns_safe_fallback_when_catalog_database_fails(self):
        with self.assertLogs("appointments.chatbot", level="WARNING") as logs:
            with patch(
                "appointments.chatbot.Service.objects.filter",
                side_effect=DatabaseError("Confidential Patient Name"),
            ):
                response = self.chat("Giá Dental check-up bao nhiêu?")

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data["intent"], "unavailable")
        self.assertIn("liên hệ lễ tân", response.data["answer"])
        self.assertNotIn("Confidential Patient Name", " ".join(logs.output))

    def test_chatbot_returns_safe_fallback_when_schedule_database_fails(self):
        work_date = timezone.localdate() + timedelta(days=10)
        question = f"Lịch Dental check-up ngày {work_date:%d/%m/%Y} còn giờ nào?"

        with patch(
            "appointments.chatbot.WorkSchedule.objects.filter",
            side_effect=DatabaseError("Confidential Patient Name"),
        ):
            response = self.chat(question)

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data["intent"], "unavailable")
        self.assertIn("thử lại sau", response.data["answer"])
        self.assertNotIn("Confidential Patient Name", response.data["answer"])

    @patch("appointments.ai_services.requests.post", side_effect=requests.ConnectionError)
    def test_chatbot_price_lookup_does_not_depend_on_ai_provider(self, provider_post):
        response = self.chat("Giá Dental check-up bao nhiêu?")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["intent"], "price")
        self.assertIn("250,000 ₫", response.data["answer"])
        provider_post.assert_not_called()


class AppointmentCancellationApiTests(TestCase):
    def setUp(self):
        receptionist_role = Role.objects.create(code="RECEPTIONIST", name="Receptionist")
        dentist_role = Role.objects.create(code="DENTIST", name="Dentist")
        receptionist = User.objects.create_user(username="front-desk", password="test-pass")
        self.dentist_user = User.objects.create_user(username="dentist", password="test-pass")
        ClinicUser.objects.create(user=receptionist, role=receptionist_role)
        dentist_profile = ClinicUser.objects.create(user=self.dentist_user, role=dentist_role)
        self.doctor = Doctor.objects.create(
            clinic_user=dentist_profile,
            license_number="CANCEL-TEST-001",
            specialization="General dentistry",
        )
        self.patient = Patient.objects.create(
            patient_code="CANCEL-TEST-001",
            full_name="Cancellation Test Patient",
        )
        self.service = Service.objects.create(
            code="CANCEL-TEST",
            name="Cancellation test",
            price="100000",
        )
        self.client = APIClient()
        self.client.force_authenticate(receptionist)

    def create_appointment(self, appointment_status):
        return Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            service=self.service,
            appointment_date=timezone.now() + timedelta(days=1),
            status=appointment_status,
        )

    def cancel(self, appointment):
        return self.client.post(f"/api/v1/appointments/{appointment.id}/cancel/")

    def test_pending_appointment_can_be_cancelled(self):
        appointment = self.create_appointment(Appointment.Status.PENDING)

        response = self.cancel(appointment)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Appointment.Status.CANCELLED)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.CANCELLED)

    def test_confirmed_appointment_can_be_cancelled(self):
        appointment = self.create_appointment(Appointment.Status.CONFIRMED)

        response = self.cancel(appointment)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Appointment.Status.CANCELLED)

    def test_already_cancelled_appointment_returns_clear_validation_error(self):
        appointment = self.create_appointment(Appointment.Status.CANCELLED)

        response = self.cancel(appointment)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data["status"]), "This appointment is already cancelled.")

    def test_completed_appointment_cannot_be_cancelled(self):
        appointment = self.create_appointment(Appointment.Status.COMPLETED)

        response = self.cancel(appointment)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data["status"]),
            "Only pending or confirmed appointments can be cancelled.",
        )
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.COMPLETED)

    def test_dentist_cannot_cancel_an_appointment(self):
        appointment = self.create_appointment(Appointment.Status.PENDING)
        self.client.force_authenticate(self.dentist_user)

        response = self.cancel(appointment)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.PENDING)


class MedicalRecordApiTests(TestCase):
    def setUp(self):
        dentist_role = Role.objects.create(code="DENTIST", name="Dentist")
        self.dentist_user = User.objects.create_user(username="record-dentist", password="test-pass")
        dentist_profile = ClinicUser.objects.create(user=self.dentist_user, role=dentist_role)
        self.doctor = Doctor.objects.create(
            clinic_user=dentist_profile,
            license_number="RECORD-TEST-001",
            specialization="General dentistry",
        )
        self.patient = Patient.objects.create(
            patient_code="RECORD-TEST-001",
            full_name="Medical Record Test Patient",
        )
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            status=Appointment.Status.CONFIRMED,
        )
        self.tooth = Tooth.objects.create(
            code="A01",
            dentition_type=Patient.ADULT,
            display_order=1,
        )
        self.service = Service.objects.create(
            code="RECORD-TEST",
            name="Medical record test service",
            price="100000",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.dentist_user)

    def test_dentist_can_create_retrieve_and_update_medical_record(self):
        create_response = self.client.post(
            "/api/v1/medical-records/",
            {
                "appointment": self.appointment.id,
                "diagnosis": "Initial diagnosis",
                "treatment_plan": "Initial treatment plan",
                "teeth": [self.tooth.id],
                "services": [self.service.id],
                "notes": "Initial examination notes",
            },
            format="json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        record_id = create_response.data["id"]
        record = MedicalRecord.objects.get(pk=record_id)
        self.assertEqual(list(record.teeth.all()), [self.tooth])
        self.assertEqual(list(record.services.all()), [self.service])
        self.assertEqual(create_response.data["tooth_codes"], ["A01"])

        retrieve_response = self.client.get(f"/api/v1/medical-records/{record_id}/")
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data["diagnosis"], "Initial diagnosis")

        update_response = self.client.patch(
            f"/api/v1/medical-records/{record_id}/",
            {
                "diagnosis": "Updated diagnosis",
                "teeth": [],
                "services": [],
            },
            format="json",
        )

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        record.refresh_from_db()
        self.assertEqual(record.diagnosis, "Updated diagnosis")
        self.assertFalse(record.teeth.exists())
        self.assertFalse(record.services.exists())

    def test_medical_record_rejects_teeth_from_another_dentition(self):
        child_tooth = Tooth.objects.create(
            code="C01",
            dentition_type=Patient.CHILD,
            display_order=1,
        )

        response = self.client.post(
            "/api/v1/medical-records/",
            {
                "appointment": self.appointment.id,
                "diagnosis": "Diagnosis",
                "treatment_plan": "Plan",
                "teeth": [child_tooth.id],
                "services": [],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Selected teeth must match", str(response.data["teeth"]))
        self.assertFalse(MedicalRecord.objects.exists())

    def test_dentist_cannot_create_record_for_another_dentists_appointment(self):
        other_user = User.objects.create_user(username="other-record-dentist", password="test-pass")
        dentist_role = Role.objects.get(code="DENTIST")
        other_profile = ClinicUser.objects.create(user=other_user, role=dentist_role)
        other_doctor = Doctor.objects.create(
            clinic_user=other_profile,
            license_number="RECORD-TEST-002",
            specialization="General dentistry",
        )
        other_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=other_doctor,
            appointment_date=timezone.now() + timedelta(days=2),
            status=Appointment.Status.CONFIRMED,
        )

        response = self.client.post(
            "/api/v1/medical-records/",
            {
                "appointment": other_appointment.id,
                "diagnosis": "Diagnosis",
                "treatment_plan": "Plan",
                "teeth": [],
                "services": [],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("only document appointments assigned to you", str(response.data["appointment"]))
        self.assertFalse(MedicalRecord.objects.exists())
