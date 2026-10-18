from datetime import datetime, time, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

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

    def test_chatbot_hands_off_urgent_medical_questions(self):
        response = self.chat("Tôi đau dữ dội và mặt đang sưng")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["intent"], "handoff")
        self.assertIn("không tư vấn y tế", response.data["answer"])

    def test_chatbot_rejects_extra_patient_data_and_oversized_question(self):
        extra_data = self.chat(
            "Giá Dental check-up?",
            {"patient_id": 1, "medical_history": "private"},
        )
        oversized = self.chat("a" * 501)

        self.assertEqual(extra_data.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(oversized.status_code, status.HTTP_400_BAD_REQUEST)

    def test_chatbot_returns_safe_fallback_when_catalog_database_fails(self):
        with patch(
            "appointments.chatbot.Service.objects.filter",
            side_effect=DatabaseError("catalog unavailable"),
        ):
            response = self.chat("Giá Dental check-up bao nhiêu?")

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data["intent"], "unavailable")
        self.assertIn("liên hệ lễ tân", response.data["answer"])


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
