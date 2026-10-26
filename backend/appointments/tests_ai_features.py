from datetime import date, timedelta
from unittest.mock import Mock, patch

import requests
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from clinic.models import ClinicUser, Doctor, Patient, Role
from .models import Appointment, FollowUpReminder, MedicalRecord


User = get_user_model()


class MedicalRecordAISummaryTests(TestCase):
    def setUp(self):
        role = Role.objects.create(code="DENTIST", name="Dentist")
        self.user = User.objects.create_user(username="ai-dentist", password="test")
        profile = ClinicUser.objects.create(user=self.user, role=role)
        doctor = Doctor.objects.create(
            clinic_user=profile,
            license_number="AI-SUMMARY-001",
        )
        patient = Patient.objects.create(
            patient_code="PAT-9001",
            full_name="An Nguyen",
            phone="0912345678",
            date_of_birth=date(1990, 1, 2),
            ai_processing_consent=True,
        )
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date=timezone.now(),
        )
        self.record = MedicalRecord.objects.create(
            appointment=appointment,
            diagnosis="An Nguyen, PAT-9001, phone 0912345678: gingivitis",
            treatment_plan="Scaling and polishing",
            prescription="",
            notes="DOB: 1990-01-02. Follow up in three months.",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.ai_services.requests.post")
    def test_summary_uses_gemini_without_direct_patient_identifiers(self, post):
        response_from_provider = Mock(status_code=200)
        response_from_provider.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "Ghi nhận: viêm lợi."}]}}
            ]
        }
        post.return_value = response_from_provider

        response = self.client.post(
            f"/api/v1/medical-records/{self.record.pk}/ai-summary/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["provider"], "Gemini")
        self.assertIn("viêm lợi", response.data["summary"])
        sent_text = post.call_args.kwargs["json"]["contents"][0]["parts"][0]["text"]
        self.assertNotIn("An Nguyen", sent_text)
        self.assertNotIn("PAT-9001", sent_text)
        self.assertNotIn("0912345678", sent_text)
        self.assertNotIn("1990-01-02", sent_text)
        self.assertNotIn("follow_up_date", sent_text)
        self.record.refresh_from_db()
        self.assertEqual(
            self.record.diagnosis,
            "An Nguyen, PAT-9001, phone 0912345678: gingivitis",
        )
        self.assertEqual(
            post.call_args.kwargs["headers"]["x-goog-api-key"],
            "test-key",
        )

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.ai_services.requests.post")
    def test_summary_redacts_common_date_formats_and_identifiers(self, post):
        patient = self.record.appointment.patient
        patient.full_name = "Nguyễn Ánh"
        patient.save(update_fields=["full_name"])
        self.record.diagnosis = (
            "Bệnh nhân Nguyễn Ánh; mã PAT-9001; DOB 01.02.1990; "
            "090 123 4567; 2024/05/06; email an.nguyen@example.com"
        )
        self.record.notes = "Người bệnh Nguyễn   Ánh, sinh 1990.01.02."
        self.record.save(update_fields=["diagnosis", "notes"])
        response_from_provider = Mock(status_code=200)
        response_from_provider.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "Ghi nhận: bệnh nhân ổn."}]}}
            ]
        }
        post.return_value = response_from_provider

        response = self.client.post(
            f"/api/v1/medical-records/{self.record.pk}/ai-summary/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sent_text = post.call_args.kwargs["json"]["contents"][0]["parts"][0]["text"]
        self.assertNotIn("An Nguyen", sent_text)
        self.assertNotIn("PAT-9001", sent_text)
        self.assertNotIn("01.02.1990", sent_text)
        self.assertNotIn("2024/05/06", sent_text)
        self.assertNotIn("090 123 4567", sent_text)
        self.assertNotIn("an.nguyen@example.com", sent_text)
        self.assertNotIn("1990.01.02", sent_text)
        self.assertNotIn("Nguyễn Ánh", sent_text)
        self.assertNotIn("Nguyễn   Ánh", sent_text)

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.views.generate_medical_record_summary", return_value="Bản nháp")
    def test_summary_is_limited_to_dentists_and_admins(self, generate_summary):
        receptionist_role = Role.objects.create(code="RECEPTIONIST", name="Receptionist")
        receptionist = User.objects.create_user(
            username="summary-receptionist",
            password="test-password",
        )
        ClinicUser.objects.create(user=receptionist, role=receptionist_role)
        receptionist_client = APIClient()
        receptionist_client.force_authenticate(receptionist)

        response = receptionist_client.post(
            f"/api/v1/medical-records/{self.record.pk}/ai-summary/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        generate_summary.assert_not_called()

    @patch("appointments.views.generate_medical_record_summary")
    def test_dentist_cannot_summarize_another_dentists_record(self, generate_summary):
        dentist_role = Role.objects.get(code="DENTIST")
        other_user = User.objects.create_user(
            username="other-summary-dentist",
            password="test-password",
        )
        other_profile = ClinicUser.objects.create(user=other_user, role=dentist_role)
        other_doctor = Doctor.objects.create(
            clinic_user=other_profile,
            license_number="AI-SUMMARY-OTHER",
        )
        other_appointment = Appointment.objects.create(
            patient=self.record.appointment.patient,
            doctor=other_doctor,
            appointment_date=timezone.now(),
        )
        other_record = MedicalRecord.objects.create(
            appointment=other_appointment,
            diagnosis="Private diagnosis",
            treatment_plan="Private treatment plan",
        )

        response = self.client.post(
            f"/api/v1/medical-records/{other_record.pk}/ai-summary/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        generate_summary.assert_not_called()

    @patch("appointments.views.generate_medical_record_summary")
    def test_summary_failure_logs_do_not_include_patient_or_clinical_data(self, generate_summary):
        from appointments.ai_services import AIServiceError

        generate_summary.side_effect = AIServiceError("Gemini returned invalid response.")

        with self.assertLogs("appointments.views", level="WARNING") as logs:
            response = self.client.post(
                f"/api/v1/medical-records/{self.record.pk}/ai-summary/",
                {},
                format="json",
            )

        log_output = " ".join(logs.output)
        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        for sensitive_value in (
            "An Nguyen",
            "PAT-9001",
            "0912345678",
            "gingivitis",
            "Scaling and polishing",
        ):
            self.assertNotIn(sensitive_value, log_output)

    @patch("appointments.ai_services.requests.post")
    def test_summary_rejects_client_supplied_clinical_content(self, post):
        response = self.client.post(
            f"/api/v1/medical-records/{self.record.pk}/ai-summary/",
            {"notes": "Do not send this field."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid_input")
        self.assertFalse(response.data["retryable"])
        post.assert_not_called()

    @patch("appointments.ai_services.requests.post")
    def test_summary_requires_recorded_patient_consent(self, post):
        self.record.appointment.patient.ai_processing_consent = False
        self.record.appointment.patient.save(update_fields=["ai_processing_consent"])

        response = self.client.post(
            f"/api/v1/medical-records/{self.record.pk}/ai-summary/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid_input")
        post.assert_not_called()

    @override_settings(GEMINI_API_KEY="")
    @patch("appointments.ai_services.requests.post")
    def test_summary_reports_unconfigured_provider(self, post):
        response = self.client.post(
            f"/api/v1/medical-records/{self.record.pk}/ai-summary/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data["code"], "ai_unavailable")
        self.assertFalse(response.data["retryable"])
        post.assert_not_called()

    @patch("appointments.views.generate_medical_record_summary")
    def test_summary_reports_timeout_as_retryable(self, generate_summary):
        from appointments.ai_services import AIServiceTimeoutError

        generate_summary.side_effect = AIServiceTimeoutError()

        response = self.client.post(
            f"/api/v1/medical-records/{self.record.pk}/ai-summary/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_504_GATEWAY_TIMEOUT)
        self.assertEqual(response.data["code"], "ai_timeout")
        self.assertTrue(response.data["retryable"])

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.ai_services.time.sleep")
    @patch("appointments.ai_services.requests.post")
    def test_slow_summary_ai_times_out_after_five_second_read_timeout(
        self, post, sleep
    ):
        post.side_effect = requests.Timeout()
        original_diagnosis = self.record.diagnosis
        original_notes = self.record.notes

        response = self.client.post(
            f"/api/v1/medical-records/{self.record.pk}/ai-summary/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_504_GATEWAY_TIMEOUT)
        self.assertEqual(response.data["code"], "ai_timeout")
        self.assertTrue(response.data["retryable"])
        self.assertEqual(post.call_count, 2)
        self.assertEqual(post.call_args.kwargs["timeout"], (3, 5))
        sleep.assert_called_once_with(0.5)
        self.record.refresh_from_db()
        self.assertEqual(self.record.diagnosis, original_diagnosis)
        self.assertEqual(self.record.notes, original_notes)

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.ai_services.requests.post")
    def test_summary_handles_missing_provider_json_fields_without_mutating_record(
        self, post
    ):
        provider_response = Mock(status_code=200)
        provider_response.json.return_value = {"candidates": [{"content": {}}]}
        post.return_value = provider_response
        original_diagnosis = self.record.diagnosis
        original_notes = self.record.notes

        with self.assertLogs("appointments.views", level="WARNING") as logs:
            response = self.client.post(
                f"/api/v1/medical-records/{self.record.pk}/ai-summary/",
                {},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(response.data["code"], "ai_generation_failed")
        self.assertTrue(response.data["retryable"])
        self.assertIn("thử lại", response.data["detail"])
        provider_response.close.assert_called_once()
        self.assertNotIn("An Nguyen", " ".join(logs.output))
        self.record.refresh_from_db()
        self.assertEqual(self.record.diagnosis, original_diagnosis)
        self.assertEqual(self.record.notes, original_notes)


@override_settings(
    TWILIO_ACCOUNT_SID="AC-test",
    TWILIO_AUTH_TOKEN="test-token",
    TWILIO_FROM_NUMBER="+15550000000",
)
class FollowUpSMSReminderTests(TestCase):
    def setUp(self):
        role = Role.objects.create(code="DENTIST", name="Dentist")
        user = User.objects.create_user(username="sms-dentist", password="test")
        profile = ClinicUser.objects.create(user=user, role=role)
        doctor = Doctor.objects.create(
            clinic_user=profile,
            license_number="SMS-REMINDER-001",
        )
        self.patient = Patient.objects.create(
            patient_code="SMS-9001",
            full_name="Reminder Patient",
            phone="0912345678",
            sms_reminder_consent=True,
        )
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=doctor,
            appointment_date=timezone.now(),
        )
        self.record = MedicalRecord.objects.create(
            appointment=appointment,
            diagnosis="Routine examination",
            treatment_plan="Follow-up as needed",
            follow_up_date=timezone.localdate(),
        )

    @patch("appointments.management.commands.send_follow_up_reminders.send_sms")
    @patch(
        "appointments.management.commands.send_follow_up_reminders.generate_generic_follow_up_text",
        return_value="Vui lòng liên hệ phòng khám.",
    )
    def test_command_sends_due_reminder_once(self, generate_text, send_sms_mock):
        send_sms_mock.return_value = "SM-test-reference"
        output = []

        call_command("send_follow_up_reminders", stdout=Mock(write=output.append))
        call_command("send_follow_up_reminders", stdout=Mock(write=output.append))

        send_sms_mock.assert_called_once()
        self.assertEqual(send_sms_mock.call_args.args[0], "0912345678")
        self.assertIn(
            f"ngày {self.record.follow_up_date:%d/%m}",
            send_sms_mock.call_args.args[1],
        )
        delivery = FollowUpReminder.objects.get(medical_record=self.record)
        self.assertEqual(delivery.status, FollowUpReminder.Status.SENT)
        self.assertEqual(delivery.provider_reference, "SM-test-reference")
        generate_text.assert_called_once()

    @patch("appointments.management.commands.send_follow_up_reminders.send_sms")
    @patch("appointments.management.commands.send_follow_up_reminders.generate_generic_follow_up_text")
    def test_command_skips_patients_without_sms_consent(self, generate_text, send_sms_mock):
        self.patient.sms_reminder_consent = False
        self.patient.save(update_fields=["sms_reminder_consent"])

        call_command("send_follow_up_reminders")

        generate_text.assert_not_called()
        send_sms_mock.assert_not_called()
        self.assertFalse(FollowUpReminder.objects.exists())

    @patch("appointments.management.commands.send_follow_up_reminders.send_sms")
    @patch(
        "appointments.management.commands.send_follow_up_reminders.generate_generic_follow_up_text",
        return_value="Vui lòng liên hệ phòng khám.",
    )
    def test_command_marks_failed_delivery_and_reports_error(self, generate_text, send_sms_mock):
        from appointments.sms_services import SMSServiceError

        send_sms_mock.side_effect = SMSServiceError("Twilio returned HTTP 400.")

        with self.assertRaises(CommandError):
            call_command("send_follow_up_reminders")

        delivery = FollowUpReminder.objects.get(medical_record=self.record)
        self.assertEqual(delivery.status, FollowUpReminder.Status.FAILED)
        self.assertIn("HTTP 400", delivery.error_message)

    @patch("appointments.management.commands.send_follow_up_reminders.send_sms")
    @patch(
        "appointments.management.commands.send_follow_up_reminders.generate_generic_follow_up_text",
        return_value="Vui lòng liên hệ phòng khám.",
    )
    def test_command_does_not_retry_an_unknown_provider_outcome(self, generate_text, send_sms_mock):
        from appointments.sms_services import SMSDeliveryUncertainError

        send_sms_mock.side_effect = SMSDeliveryUncertainError(
            "Twilio request outcome is unknown; verify the provider before retrying."
        )

        with self.assertRaises(CommandError):
            call_command("send_follow_up_reminders")

        delivery = FollowUpReminder.objects.get(medical_record=self.record)
        self.assertEqual(delivery.status, FollowUpReminder.Status.UNKNOWN)
        with self.assertRaises(CommandError):
            call_command("send_follow_up_reminders")
        send_sms_mock.assert_called_once()
        generate_text.assert_called_once()

    @patch("appointments.management.commands.send_follow_up_reminders.send_sms")
    @patch("appointments.management.commands.send_follow_up_reminders.generate_generic_follow_up_text")
    def test_dry_run_does_not_call_external_services(self, generate_text, send_sms_mock):
        call_command("send_follow_up_reminders", "--dry-run")

        generate_text.assert_not_called()
        send_sms_mock.assert_not_called()
        self.assertFalse(FollowUpReminder.objects.exists())

    @override_settings(
        TWILIO_ACCOUNT_SID="",
        TWILIO_AUTH_TOKEN="",
        TWILIO_FROM_NUMBER="",
    )
    @patch("appointments.management.commands.send_follow_up_reminders.send_sms")
    @patch("appointments.management.commands.send_follow_up_reminders.generate_generic_follow_up_text")
    def test_command_requires_twilio_configuration_before_calling_gemini(self, generate_text, send_sms_mock):
        with self.assertRaises(CommandError):
            call_command("send_follow_up_reminders")

        generate_text.assert_not_called()
        send_sms_mock.assert_not_called()


class TwilioSMSServiceTests(TestCase):
    @override_settings(
        TWILIO_ACCOUNT_SID="AC-test",
        TWILIO_AUTH_TOKEN="test-token",
        TWILIO_FROM_NUMBER="+15550000000",
    )
    @patch("appointments.sms_services.requests.post")
    def test_sms_sends_short_reminder_to_normalized_phone(self, post):
        from .sms_services import send_sms

        response = Mock(status_code=201)
        response.json.return_value = {"sid": "SM-test-reference"}
        post.return_value = response

        reference = send_sms("0912345678", "Mời bạn tái khám ngày 18/10.")

        self.assertEqual(reference, "SM-test-reference")
        self.assertEqual(post.call_args.kwargs["data"]["To"], "+84912345678")
        self.assertEqual(post.call_args.kwargs["data"]["From"], "+15550000000")
        self.assertEqual(post.call_args.kwargs["data"]["Body"], "Mời bạn tái khám ngày 18/10.")

    @override_settings(
        TWILIO_ACCOUNT_SID="AC-test",
        TWILIO_AUTH_TOKEN="test-token",
        TWILIO_FROM_NUMBER="+15550000000",
    )
    @patch("appointments.sms_services.requests.post")
    def test_sms_rejects_invalid_phone_without_calling_provider(self, post):
        from .sms_services import SMSServiceError, send_sms

        with self.assertRaises(SMSServiceError):
            send_sms("not-a-phone", "Mời bạn tái khám.")

        post.assert_not_called()


class FollowUpReminderPreviewTests(TestCase):
    def setUp(self):
        cache.clear()
        receptionist_role = Role.objects.create(
            code="RECEPTIONIST",
            name="Receptionist",
        )
        dentist_role = Role.objects.create(code="DENTIST", name="Dentist")
        receptionist = User.objects.create_user(
            username="reminder-receptionist",
            password="ReceptionPass123!",
        )
        dentist_user = User.objects.create_user(
            username="reminder-dentist",
            password="DentistPass123!",
            first_name="Linh",
            last_name="Dentist",
        )
        ClinicUser.objects.create(user=receptionist, role=receptionist_role)
        dentist_profile = ClinicUser.objects.create(
            user=dentist_user,
            role=dentist_role,
        )
        self.doctor = Doctor.objects.create(
            clinic_user=dentist_profile,
            license_number="REMINDER-API-001",
        )
        self.receptionist = receptionist
        self.patient = Patient.objects.create(
            patient_code="REMINDER-API-001",
            full_name="Private Reminder Patient",
            phone="0912345678",
            sms_reminder_consent=True,
        )
        self.record = self.create_record(self.patient, date(2026, 11, 3))
        self.client = APIClient()
        self.client.force_authenticate(receptionist)

    def create_record(self, patient, follow_up_date):
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=self.doctor,
            appointment_date=timezone.now(),
        )
        return MedicalRecord.objects.create(
            appointment=appointment,
            diagnosis="Private diagnosis",
            treatment_plan="Private treatment plan",
            follow_up_date=follow_up_date,
        )

    def test_follow_up_list_returns_selected_fields_without_clinical_data(self):
        no_consent_patient = Patient.objects.create(
            patient_code="REMINDER-API-002",
            full_name="No Consent Patient",
            sms_reminder_consent=False,
        )
        no_consent_record = self.create_record(
            no_consent_patient,
            date(2026, 11, 5),
        )
        missing_date_patient = Patient.objects.create(
            patient_code="REMINDER-API-003",
            full_name="Missing Date Patient",
            sms_reminder_consent=True,
        )
        self.create_record(missing_date_patient, None)

        response = self.client.get("/api/v1/follow-up-appointments/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {item["id"] for item in response.data},
            {self.record.pk, no_consent_record.pk},
        )
        self.assertEqual(response.data[0]["follow_up_date"], "2026-11-03")
        self.assertIn("sms_reminder_consent", response.data[0])
        self.assertNotIn("diagnosis", response.data[0])
        self.assertNotIn("phone", response.data[0])

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch(
        "appointments.views.generate_generic_follow_up_text",
        return_value="Vui lòng liên hệ phòng khám.",
    )
    def test_preview_uses_saved_date_and_returns_unsent_message(self, generate_text):
        response = self.client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": self.record.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data["follow_up_date"]), "2026-11-03")
        self.assertEqual(
            response.data["message"],
            "Mời bạn tái khám ngày 03/11. Vui lòng liên hệ phòng khám.",
        )
        self.assertEqual(response.data["provider"], "Gemini")
        self.assertFalse(response.data["sent"])
        self.assertFalse(FollowUpReminder.objects.filter(medical_record=self.record).exists())
        generate_text.assert_called_once_with()

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.sms_services.send_sms")
    @patch("appointments.ai_services.requests.post")
    def test_preview_api_keeps_patient_and_appointment_data_out_of_ai_request(
        self, post, send_sms
    ):
        provider_response = Mock(status_code=200)
        provider_response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "Vui lòng liên hệ phòng khám."}]}}
            ]
        }
        post.return_value = provider_response

        response = self.client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": self.record.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"],
            "Mời bạn tái khám ngày 03/11. Vui lòng liên hệ phòng khám.",
        )
        self.assertFalse(response.data["sent"])
        self.assertFalse(FollowUpReminder.objects.filter(medical_record=self.record).exists())
        send_sms.assert_not_called()
        provider_request = str(post.call_args.kwargs["json"])
        for sensitive_value in (
            "Private Reminder Patient",
            "REMINDER-API-001",
            "0912345678",
            "2026-11-03",
            "Private diagnosis",
            "Private treatment plan",
        ):
            self.assertNotIn(sensitive_value, provider_request)

    @patch(
        "appointments.views.generate_generic_follow_up_text",
        return_value="Vui lòng liên hệ phòng khám.",
    )
    def test_preview_requests_for_multiple_records_keep_dates_isolated(self, generate_text):
        second_patient = Patient.objects.create(
            patient_code="REMINDER-API-006",
            full_name="Second Reminder Patient",
            sms_reminder_consent=True,
        )
        second_record = self.create_record(second_patient, date(2026, 12, 4))

        first_response = self.client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": self.record.pk},
            format="json",
        )
        second_response = self.client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": second_record.pk},
            format="json",
        )

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(first_response.data["follow_up_date"]), "2026-11-03")
        self.assertEqual(str(second_response.data["follow_up_date"]), "2026-12-04")
        self.assertIn("03/11", first_response.data["message"])
        self.assertIn("04/12", second_response.data["message"])
        self.assertFalse(FollowUpReminder.objects.exists())
        self.assertEqual(generate_text.call_count, 2)

    @patch(
        "appointments.views.generate_generic_follow_up_text",
        return_value="Vui lòng liên hệ phòng khám.",
    )
    def test_preview_is_rate_limited_per_authenticated_user(self, generate_text):
        for _ in range(10):
            response = self.client.post(
                "/api/ai/generate-reminder",
                {"medical_record_id": self.record.pk},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        limited_response = self.client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": self.record.pk},
            format="json",
        )

        self.assertEqual(
            limited_response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )
        self.assertEqual(limited_response.data["code"], "rate_limited")
        self.assertTrue(limited_response.data["retryable"])
        self.assertIn("Retry-After", limited_response)
        self.assertEqual(generate_text.call_count, 10)

    @patch("appointments.views.generate_generic_follow_up_text")
    def test_preview_rejects_unconsented_patient(self, generate_text):
        self.patient.sms_reminder_consent = False
        self.patient.save(update_fields=["sms_reminder_consent"])

        response = self.client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": self.record.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        generate_text.assert_not_called()

    @patch("appointments.views.generate_generic_follow_up_text")
    def test_preview_rejects_record_without_follow_up_date(self, generate_text):
        patient = Patient.objects.create(
            patient_code="REMINDER-API-004",
            full_name="No Follow-up Date",
            sms_reminder_consent=True,
        )
        record = self.create_record(patient, None)

        response = self.client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": record.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        generate_text.assert_not_called()

    @patch("appointments.views.generate_generic_follow_up_text")
    def test_preview_rejects_invalid_ids_and_client_supplied_data(self, generate_text):
        invalid_id = self.client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": "invalid"},
            format="json",
        )
        extra_data = self.client.post(
            "/api/ai/generate-reminder",
            {
                "medical_record_id": self.record.pk,
                "follow_up_date": "2099-01-01",
                "patient_name": "Untrusted Name",
            },
            format="json",
        )
        missing_id = self.client.post(
            "/api/ai/generate-reminder",
            {},
            format="json",
        )

        self.assertEqual(invalid_id.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(extra_data.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(missing_id.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(invalid_id.data["code"], "invalid_input")
        self.assertFalse(invalid_id.data["retryable"])
        generate_text.assert_not_called()

    @patch("appointments.views.generate_generic_follow_up_text")
    def test_preview_returns_not_found_for_unknown_record(self, generate_text):
        response = self.client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": 999999},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["code"], "record_not_found")
        generate_text.assert_not_called()

    @override_settings(GEMINI_API_KEY="")
    @patch("appointments.ai_services.requests.post")
    def test_preview_reports_missing_ai_configuration(self, post):
        response = self.client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": self.record.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data["code"], "ai_unavailable")
        post.assert_not_called()

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.ai_services.requests.post")
    def test_preview_reports_empty_or_invalid_ai_output(self, post):
        provider_response = Mock(status_code=200)
        provider_response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": ""}]}}
            ]
        }
        post.return_value = provider_response
        response = self.client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": self.record.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(response.data["code"], "ai_generation_failed")
        self.assertTrue(response.data["retryable"])
        self.assertFalse(FollowUpReminder.objects.filter(medical_record=self.record).exists())
        provider_response.close.assert_called_once()

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.ai_services.requests.post")
    def test_preview_rejects_malformed_json_and_missing_provider_fields(self, post):
        malformed_json = Mock(status_code=200)
        malformed_json.json.side_effect = ValueError("invalid JSON")
        missing_fields = Mock(status_code=200)
        missing_fields.json.return_value = {"candidates": [{}]}
        post.side_effect = [malformed_json, missing_fields]

        for _ in range(2):
            response = self.client.post(
                "/api/ai/generate-reminder",
                {"medical_record_id": self.record.pk},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
            self.assertEqual(response.data["code"], "ai_generation_failed")
            self.assertTrue(response.data["retryable"])

        malformed_json.close.assert_called_once()
        missing_fields.close.assert_called_once()
        self.record.refresh_from_db()
        self.assertEqual(self.record.follow_up_date, date(2026, 11, 3))
        self.assertEqual(self.record.diagnosis, "Private diagnosis")
        self.assertFalse(FollowUpReminder.objects.filter(medical_record=self.record).exists())

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.ai_services.time.sleep")
    @patch("appointments.ai_services.requests.post")
    def test_preview_timeout_returns_fallback_and_preserves_reminder_data(
        self, post, sleep
    ):
        post.side_effect = requests.Timeout()

        response = self.client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": self.record.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_504_GATEWAY_TIMEOUT)
        self.assertEqual(response.data["code"], "ai_timeout")
        self.assertTrue(response.data["retryable"])
        self.assertIn("thử lại", response.data["detail"])
        self.assertEqual(post.call_count, 2)
        self.assertEqual(post.call_args.kwargs["timeout"], (3, 5))
        sleep.assert_called_once_with(0.5)
        self.record.refresh_from_db()
        self.assertEqual(self.record.follow_up_date, date(2026, 11, 3))
        self.assertFalse(FollowUpReminder.objects.filter(medical_record=self.record).exists())

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.ai_services.time.sleep")
    @patch("appointments.ai_services.requests.post")
    def test_preview_connection_failure_returns_safe_unavailable_response(
        self, post, sleep
    ):
        post.side_effect = requests.ConnectionError()

        response = self.client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": self.record.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data["code"], "ai_unavailable")
        self.assertTrue(response.data["retryable"])
        self.assertIn("thử lại sau", response.data["detail"])
        self.assertEqual(post.call_count, 2)
        sleep.assert_called_once_with(0.5)
        self.record.refresh_from_db()
        self.assertEqual(self.record.follow_up_date, date(2026, 11, 3))
        self.assertFalse(FollowUpReminder.objects.filter(medical_record=self.record).exists())

    @patch("appointments.views.generate_generic_follow_up_text")
    def test_preview_reports_temporary_service_failure_as_retryable(self, generate_text):
        from appointments.ai_services import AIServiceUnavailableError

        generate_text.side_effect = AIServiceUnavailableError()

        response = self.client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": self.record.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data["code"], "ai_unavailable")
        self.assertTrue(response.data["retryable"])

    @patch("appointments.views.generate_generic_follow_up_text")
    def test_preview_reports_timeout_as_retryable(self, generate_text):
        from appointments.ai_services import AIServiceTimeoutError

        generate_text.side_effect = AIServiceTimeoutError()

        response = self.client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": self.record.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_504_GATEWAY_TIMEOUT)
        self.assertEqual(response.data["code"], "ai_timeout")
        self.assertTrue(response.data["retryable"])

    @patch("appointments.views.generate_generic_follow_up_text")
    def test_preview_failure_logs_do_not_include_patient_or_clinical_data(self, generate_text):
        from appointments.ai_services import AIServiceError

        generate_text.side_effect = AIServiceError("Gemini returned invalid response.")

        with self.assertLogs("appointments.views", level="WARNING") as logs:
            response = self.client.post(
                "/api/ai/generate-reminder",
                {"medical_record_id": self.record.pk},
                format="json",
            )

        log_output = " ".join(logs.output)
        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        for sensitive_value in (
            "Private Reminder Patient",
            "REMINDER-API-001",
            "0912345678",
            "Private diagnosis",
            "Private treatment plan",
        ):
            self.assertNotIn(sensitive_value, log_output)

    def test_preview_does_not_generate_for_cancelled_appointment(self):
        patient = Patient.objects.create(
            patient_code="REMINDER-API-005",
            full_name="Cancelled Follow-up",
            sms_reminder_consent=True,
        )
        record = self.create_record(patient, date(2026, 11, 6))
        record.appointment.status = Appointment.Status.CANCELLED
        record.appointment.save(update_fields=["status"])

        response = self.client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": record.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch(
        "appointments.views.generate_generic_follow_up_text",
        return_value="Liên hệ phòng khám để được hỗ trợ thêm nhé.",
    )
    def test_preview_rejects_message_over_single_sms_limit(self, generate_text):
        response = self.client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": self.record.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)

    def test_only_receptionist_or_admin_can_manage_follow_up_reminders(self):
        dentist_role = Role.objects.get(code="DENTIST")
        dentist = User.objects.create_user(
            username="reminder-unauthorized-dentist",
            password="DentistPass123!",
        )
        ClinicUser.objects.create(user=dentist, role=dentist_role)
        dentist_client = APIClient()
        dentist_client.force_authenticate(dentist)

        list_response = dentist_client.get("/api/v1/follow-up-appointments/")
        preview_response = dentist_client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": self.record.pk},
            format="json",
        )

        self.assertEqual(list_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(preview_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reminder_endpoints_require_authentication(self):
        client = APIClient()

        list_response = client.get("/api/v1/follow-up-appointments/")
        preview_response = client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": self.record.pk},
            format="json",
        )

        self.assertEqual(list_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(preview_response.status_code, status.HTTP_401_UNAUTHORIZED)


class FollowUpReminderPromptTests(TestCase):
    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.ai_services.requests.post")
    def test_generic_prompt_is_separate_and_contains_no_patient_or_date_data(self, post):
        from appointments.ai_services import generate_generic_follow_up_text

        response = Mock(status_code=200)
        response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "Vui lòng liên hệ phòng khám."}]}}
            ]
        }
        post.return_value = response

        message = generate_generic_follow_up_text()

        self.assertEqual(message, "Vui lòng liên hệ phòng khám.")
        request_data = post.call_args.kwargs["json"]
        self.assertIn("system_instruction", request_data)
        self.assertNotIn("Private Reminder Patient", str(request_data))
        self.assertNotIn("2026-11-03", str(request_data))
        self.assertIn("không đưa ra ngày", request_data["contents"][0]["parts"][0]["text"])
        self.assertEqual(post.call_args.kwargs["timeout"], (3, 5))

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.ai_services.requests.post")
    def test_generic_prompt_rejects_ai_output_containing_numbers(self, post):
        from appointments.ai_services import AIServiceError, generate_generic_follow_up_text

        response = Mock(status_code=200)
        response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "Liên hệ phòng khám số 123."}]}}
            ]
        }
        post.return_value = response

        with self.assertRaises(AIServiceError):
            generate_generic_follow_up_text()


class AIServiceRetryTests(TestCase):
    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.ai_services.time.sleep")
    @patch("appointments.ai_services.requests.post")
    def test_timeout_is_retried_once_then_returns_success(self, post, sleep):
        from appointments.ai_services import _generate_text

        response = Mock(status_code=200)
        response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "summary"}]}}
            ]
        }
        post.side_effect = [requests.Timeout(), response]

        self.assertEqual(_generate_text("prompt", 20), "summary")

        self.assertEqual(post.call_count, 2)
        self.assertEqual(post.call_args.kwargs["timeout"], (3, 5))
        response.close.assert_called_once()
        sleep.assert_called_once_with(0.5)

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.ai_services.time.sleep")
    @patch("appointments.ai_services.requests.post")
    def test_timeout_after_maximum_attempts_returns_timeout_error(self, post, sleep):
        from appointments.ai_services import AIServiceTimeoutError, _generate_text

        post.side_effect = requests.Timeout()

        with self.assertRaises(AIServiceTimeoutError):
            _generate_text("prompt", 20)

        self.assertEqual(post.call_count, 2)
        self.assertEqual(sleep.call_count, 1)

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.ai_services.requests.post")
    def test_malformed_provider_json_and_missing_fields_raise_output_error(self, post):
        from appointments.ai_services import AIServiceOutputError, _generate_text

        malformed_json = Mock(status_code=200)
        malformed_json.json.side_effect = ValueError("invalid JSON")
        missing_fields = Mock(status_code=200)
        missing_fields.json.return_value = {"candidates": [{}]}
        post.side_effect = [malformed_json, missing_fields]

        for _ in range(2):
            with self.assertRaises(AIServiceOutputError):
                _generate_text("prompt", 20)

        malformed_json.close.assert_called_once()
        missing_fields.close.assert_called_once()

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.ai_services.requests.post")
    def test_empty_provider_text_raises_output_error_and_closes_response(self, post):
        from appointments.ai_services import AIServiceOutputError, _generate_text

        response = Mock(status_code=200)
        response.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "  "}]}}]
        }
        post.return_value = response

        with self.assertRaises(AIServiceOutputError):
            _generate_text("prompt", 20)

        response.close.assert_called_once()

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.ai_services.time.sleep")
    @patch("appointments.ai_services.requests.post")
    def test_connection_error_is_retried_once_then_returns_success(self, post, sleep):
        from appointments.ai_services import _generate_text

        response = Mock(status_code=200)
        response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "reconnected"}]}}
            ]
        }
        post.side_effect = [requests.ConnectionError(), response]

        self.assertEqual(_generate_text("prompt", 20), "reconnected")

        self.assertEqual(post.call_count, 2)
        sleep.assert_called_once_with(0.5)

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.ai_services.time.sleep")
    @patch("appointments.ai_services.requests.post")
    def test_transient_http_error_is_retried_once(self, post, sleep):
        from appointments.ai_services import _generate_text

        unavailable = Mock(status_code=503)
        available = Mock(status_code=200)
        available.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "recovered"}]}}
            ]
        }
        post.side_effect = [unavailable, available]

        self.assertEqual(_generate_text("prompt", 20), "recovered")

        self.assertEqual(post.call_count, 2)
        unavailable.close.assert_called_once()
        sleep.assert_called_once_with(0.5)

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.ai_services.time.sleep")
    @patch("appointments.ai_services.requests.post")
    def test_unavailable_provider_after_maximum_attempts_raises(self, post, sleep):
        from appointments.ai_services import AIServiceUnavailableError, _generate_text

        post.side_effect = [Mock(status_code=503), Mock(status_code=503)]

        with self.assertRaises(AIServiceUnavailableError):
            _generate_text("prompt", 20)

        self.assertEqual(post.call_count, 2)
        self.assertEqual(sleep.call_count, 1)

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
    @patch("appointments.ai_services.time.sleep")
    @patch("appointments.ai_services.requests.post")
    def test_permanent_http_error_is_not_retried(self, post, sleep):
        from appointments.ai_services import AIServiceError, _generate_text

        post.return_value = Mock(status_code=400)

        with self.assertRaises(AIServiceError):
            _generate_text("prompt", 20)

        post.assert_called_once()
        sleep.assert_not_called()
