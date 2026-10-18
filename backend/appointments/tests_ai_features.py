from datetime import timedelta
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
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
        self.assertEqual(
            post.call_args.kwargs["headers"]["x-goog-api-key"],
            "test-key",
        )

    @patch("appointments.ai_services.requests.post")
    def test_summary_rejects_client_supplied_clinical_content(self, post):
        response = self.client.post(
            f"/api/v1/medical-records/{self.record.pk}/ai-summary/",
            {"notes": "Do not send this field."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
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
        post.assert_not_called()


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
