from datetime import timedelta
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from appointments.models import Appointment as ScheduledAppointment, MedicalRecord
from .models import ClinicUser, Doctor, Invoice, Patient, Payment, Role


User = get_user_model()


@override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="gemini-test")
class ReminderPreviewTests(TestCase):
    def setUp(self):
        reception_role = Role.objects.create(code="RECEPTIONIST", name="Receptionist")
        reception_user = User.objects.create_user(
            username="demo-reception",
            password="Synthetic-Test-Password-123!",
        )
        ClinicUser.objects.create(user=reception_user, role=reception_role)
        dentist_role = Role.objects.create(code="DENTIST", name="Dentist")
        dentist_user = User.objects.create_user(
            username="demo-dentist",
            password="Synthetic-Test-Password-123!",
        )
        dentist_profile = ClinicUser.objects.create(user=dentist_user, role=dentist_role)
        doctor = Doctor.objects.create(
            clinic_user=dentist_profile,
            license_number="DEMO-PREVIEW-001",
        )
        self.patient = Patient.objects.create(
            patient_code="DEMO-PREVIEW-001",
            full_name="Synthetic Preview Patient",
            phone="0900000000",
            sms_reminder_consent=True,
        )
        appointment = ScheduledAppointment.objects.create(
            patient=self.patient,
            doctor=doctor,
            appointment_date=timezone.now(),
        )
        self.record = MedicalRecord.objects.create(
            appointment=appointment,
            diagnosis="Synthetic diagnosis must not be sent for reminder text.",
            treatment_plan="Synthetic treatment",
            follow_up_date=timezone.localdate() + timedelta(days=7),
        )
        self.client = APIClient()
        self.client.force_authenticate(reception_user)

    @patch("appointments.ai_services.requests.post")
    def test_receptionist_can_preview_generic_reminder_without_sending_sms_data(self, provider_post):
        provider_response = Mock(status_code=200)
        provider_response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "Vui lòng liên hệ phòng khám."}]}}
            ]
        }
        provider_post.return_value = provider_response

        response = self.client.post(
            f"/api/v1/patients/{self.patient.pk}/reminder-preview/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["provider"], "Gemini")
        self.assertFalse(response.data["sent"])
        self.assertEqual(str(response.data["follow_up_date"]), self.record.follow_up_date.isoformat())
        self.assertIn("Vui lòng liên hệ phòng khám.", response.data["message"])
        self.assertEqual(
            set(response.data),
            {"message", "follow_up_date", "provider", "sent"},
        )
        prompt = provider_post.call_args.kwargs["json"]["contents"][0]["parts"][0]["text"]
        self.assertNotIn(self.patient.full_name, prompt)
        self.assertNotIn(self.patient.phone, prompt)
        self.assertNotIn(self.patient.patient_code, prompt)
        self.assertNotIn("Synthetic diagnosis", prompt)
        self.assertFalse(MedicalRecord.objects.filter(
            appointment__patient=self.patient,
            follow_up_reminders__isnull=False,
        ).exists())

    @patch("appointments.ai_services.requests.post")
    def test_preview_requires_sms_consent_and_never_calls_provider_without_it(self, provider_post):
        self.patient.sms_reminder_consent = False
        self.patient.save(update_fields=["sms_reminder_consent"])

        response = self.client.post(
            f"/api/v1/patients/{self.patient.pk}/reminder-preview/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        provider_post.assert_not_called()

    @patch("appointments.ai_services.requests.post")
    def test_preview_requires_a_follow_up_date(self, provider_post):
        self.record.follow_up_date = None
        self.record.save(update_fields=["follow_up_date"])

        response = self.client.post(
            f"/api/v1/patients/{self.patient.pk}/reminder-preview/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        provider_post.assert_not_called()

    @patch("appointments.ai_services.requests.post")
    def test_preview_rejects_a_dentist_role(self, provider_post):
        dentist_user = User.objects.get(username="demo-dentist")
        self.client.force_authenticate(dentist_user)

        response = self.client.post(
            f"/api/v1/patients/{self.patient.pk}/reminder-preview/",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        provider_post.assert_not_called()


@override_settings(AUTH_PASSWORD_VALIDATORS=[])
class DemoDataSeedTests(TestCase):
    @patch.dict("os.environ", {"DMS_SEED_DEMO_PASSWORD": "Synthetic-Demo-Password-2026!"})
    def test_seed_creates_login_accounts_and_linked_synthetic_clinical_demo_data(self):
        call_command("seed_dental_data", stdout=Mock())

        self.assertTrue(User.objects.get(username="admin").check_password("Synthetic-Demo-Password-2026!"))
        self.assertTrue(User.objects.get(username="doctor1").check_password("Synthetic-Demo-Password-2026!"))
        self.assertTrue(User.objects.get(username="doctor2").check_password("Synthetic-Demo-Password-2026!"))
        self.assertTrue(User.objects.get(username="receptionist1").check_password("Synthetic-Demo-Password-2026!"))

        patient = Patient.objects.get(patient_code="DMS-0001")
        record = MedicalRecord.objects.get(appointment__patient=patient)
        invoice = Invoice.objects.get(medical_record=record)
        self.assertEqual(invoice.status, Invoice.ISSUED)
        self.assertEqual(invoice.total_amount, invoice.items.get().amount)
        self.assertIn("Fictional training data", record.notes)
        self.assertGreater(record.follow_up_date, timezone.localdate())
        self.assertFalse(patient.ai_processing_consent)
        self.assertFalse(patient.sms_reminder_consent)
        self.assertEqual(patient.phone, "09 35XX X001")
        self.assertEqual(
            set(Patient.objects.values_list("phone", flat=True)),
            {
                "09 35XX X001",
                "09 54XX X002",
                "09 89XX X003",
                "09 35XX X004",
                "09 54XX X005",
            },
        )
        self.assertEqual(
            ClinicUser.objects.get(user__username="doctor1").phone,
            "09 54XX X902",
        )

    def test_seed_is_idempotent_for_linked_demo_records(self):
        call_command("seed_dental_data", stdout=Mock())
        call_command("seed_dental_data", stdout=Mock())

        self.assertEqual(
            MedicalRecord.objects.filter(
                appointment__patient__patient_code="DMS-0001"
            ).count(),
            1,
        )
        self.assertEqual(
            Invoice.objects.filter(invoice_number="DEMO-INV-001").count(),
            1,
        )

    def test_seed_does_not_reset_demo_invoice_after_a_payment_exists(self):
        call_command("seed_dental_data", stdout=Mock())
        invoice = Invoice.objects.get(invoice_number="DEMO-INV-001")
        Payment.objects.create(
            invoice=invoice,
            amount=invoice.total_amount,
            method=Payment.CASH,
            status=Payment.COMPLETED,
        )
        invoice.paid_amount = invoice.total_amount
        invoice.status = Invoice.PAID
        invoice.save(update_fields=["paid_amount", "status"])

        call_command("seed_dental_data", stdout=Mock())

        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.PAID)
        self.assertEqual(invoice.paid_amount, invoice.total_amount)
        self.assertEqual(invoice.payments.count(), 1)
