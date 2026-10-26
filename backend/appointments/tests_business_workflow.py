from datetime import datetime, time, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from clinic.models import (
    ActiveInvoicePayment,
    BankTransferVerification,
    ClinicUser,
    Doctor,
    Invoice,
    InvoiceItem,
    Patient,
    Payment,
    Role,
    Service,
    Tooth,
    WorkSchedule,
)
from .ai_services import AIServiceError, AIServiceTimeoutError
from .models import Appointment, FollowUpReminder, MedicalRecord


User = get_user_model()


@override_settings(
    GEMINI_API_KEY="workflow-test-key",
    GEMINI_MODEL="gemini-test",
    VIETQR_BANK_ID="MB",
    VIETQR_ACCOUNT_NUMBER="0123456789",
    VIETQR_ACCOUNT_NAME="LOTUS DENTAL",
)
class DentalBusinessWorkflowTests(TestCase):
    def setUp(self):
        receptionist_role = Role.objects.create(
            code="RECEPTIONIST",
            name="Receptionist",
        )
        dentist_role = Role.objects.create(code="DENTIST", name="Dentist")
        receptionist = User.objects.create_user(
            username="workflow-receptionist",
            password="WorkflowPass123!",
        )
        dentist = User.objects.create_user(
            username="workflow-dentist",
            password="WorkflowPass123!",
            first_name="Workflow",
            last_name="Dentist",
        )
        self.receptionist = receptionist
        self.receptionist_profile = ClinicUser.objects.create(
            user=receptionist,
            role=receptionist_role,
        )
        dentist_profile = ClinicUser.objects.create(user=dentist, role=dentist_role)
        self.doctor = Doctor.objects.create(
            clinic_user=dentist_profile,
            license_number="WORKFLOW-DENTIST-001",
            specialization="General dentistry",
        )
        self.service = Service.objects.create(
            code="WORKFLOW-CHECKUP",
            name="Workflow dental check-up",
            price=Decimal("250000.00"),
            duration_minutes=30,
        )
        self.tooth = Tooth.objects.create(
            code="A01",
            dentition_type=Patient.ADULT,
            display_order=1,
        )
        self.appointment_date = timezone.localdate() + timedelta(days=7)
        self.appointment_start = timezone.make_aware(
            datetime.combine(self.appointment_date, time(9, 0))
        )
        self.follow_up_date = self.appointment_date + timedelta(days=14)
        WorkSchedule.objects.create(
            doctor=self.doctor,
            work_date=self.appointment_date,
            start_time=time(9, 0),
            end_time=time(10, 0),
        )
        self.receptionist_client = APIClient()
        self.receptionist_client.force_authenticate(receptionist)
        self.dentist_client = APIClient()
        self.dentist_client.force_authenticate(dentist)

    @staticmethod
    def provider_response(text):
        response = Mock(status_code=200)
        response.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": text}]}}]
        }
        return response

    def create_patient(self):
        response = self.receptionist_client.post(
            "/api/v1/patients/",
            {
                "patient_code": "WORKFLOW-PATIENT-001",
                "full_name": "Workflow Test Patient",
                "phone": "0901234567",
                "date_of_birth": "1990-05-21",
                "dentition_type": Patient.ADULT,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        patient_id = response.data["id"]

        consent_response = self.receptionist_client.patch(
            f"/api/v1/patients/{patient_id}/",
            {"ai_processing_consent": True, "sms_reminder_consent": True},
            format="json",
        )
        self.assertEqual(consent_response.status_code, status.HTTP_200_OK)
        return Patient.objects.get(pk=patient_id)

    def appointment_payload(self, patient, appointment_date=None):
        return {
            "patient": patient.pk,
            "doctor": self.doctor.pk,
            "service": self.service.pk,
            "appointment_date": (
                appointment_date or self.appointment_start
            ).isoformat(),
            "notes": "Routine check-up",
        }

    def book_appointment(self, patient):
        response = self.receptionist_client.post(
            "/api/v1/appointments/",
            self.appointment_payload(patient),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Appointment.Status.PENDING)
        return Appointment.objects.get(pk=response.data["id"])

    def create_medical_record(self, appointment):
        response = self.dentist_client.post(
            "/api/v1/medical-records/",
            {
                "appointment": appointment.pk,
                "diagnosis": "Initial assessment",
                "treatment_plan": "Assess the affected tooth",
                "prescription": "Awaiting the dentist's plan",
                "notes": "Initial examination notes.",
                "teeth": [self.tooth.pk],
                "services": [self.service.pk],
                "follow_up_date": self.follow_up_date.isoformat(),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        record = MedicalRecord.objects.get(pk=response.data["id"])
        self.assertEqual(record.appointment_id, appointment.pk)
        self.assertEqual(list(record.services.all()), [self.service])
        self.assertEqual(list(record.teeth.all()), [self.tooth])

        update_response = self.dentist_client.patch(
            f"/api/v1/medical-records/{record.pk}/",
            {
                "diagnosis": "Dental caries",
                "treatment_plan": "Restore the affected tooth",
                "prescription": "Follow the clinician's instructions",
                "notes": "No immediate complications.",
                "services": [self.service.pk],
            },
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        record.refresh_from_db()
        self.assertEqual(record.diagnosis, "Dental caries")
        self.assertEqual(record.treatment_plan, "Restore the affected tooth")
        return record

    def create_ai_outputs(self, record, provider_post):
        provider_post.side_effect = [
            self.provider_response("Ghi nhận: sâu răng; kế hoạch: phục hồi."),
            self.provider_response("Vui lòng liên hệ phòng khám."),
        ]
        summary_response = self.dentist_client.post(
            f"/api/v1/medical-records/{record.pk}/ai-summary/",
            {},
            format="json",
        )
        self.assertEqual(summary_response.status_code, status.HTTP_200_OK)
        self.assertIn("sâu răng", summary_response.data["summary"])

        reminder_response = self.receptionist_client.post(
            "/api/ai/generate-reminder",
            {"medical_record_id": record.pk},
            format="json",
        )
        self.assertEqual(reminder_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            str(reminder_response.data["follow_up_date"]),
            self.follow_up_date.isoformat(),
        )
        self.assertIn(
            self.follow_up_date.strftime("%d/%m"),
            reminder_response.data["message"],
        )
        self.assertFalse(reminder_response.data["sent"])
        self.assertEqual(provider_post.call_count, 2)
        self.assertFalse(FollowUpReminder.objects.filter(medical_record=record).exists())
        return summary_response, reminder_response

    def create_invoice(self, record, items):
        return self.receptionist_client.post(
            "/api/v1/invoices/",
            {"medical_record": record.pk, "items": items},
            format="json",
        )

    def test_patient_to_cash_payment_workflow_keeps_records_consistent(self):
        patient = self.create_patient()
        appointment = self.book_appointment(patient)
        appointment_response = self.dentist_client.get(
            f"/api/v1/appointments/{appointment.pk}/"
        )
        self.assertEqual(appointment_response.status_code, status.HTTP_200_OK)
        self.assertEqual(appointment_response.data["patient"], patient.pk)

        record = self.create_medical_record(appointment)
        with patch("appointments.ai_services.requests.post") as provider_post, patch(
            "appointments.sms_services.send_sms"
        ) as send_sms:
            summary_response, reminder_response = self.create_ai_outputs(
                record,
                provider_post,
            )
        send_sms.assert_not_called()

        self.assertEqual(summary_response.data["provider"], "Gemini")
        self.assertEqual(reminder_response.data["medical_record_id"], record.pk)
        record.refresh_from_db()
        self.assertEqual(record.diagnosis, "Dental caries")
        self.assertEqual(record.appointment_id, appointment.pk)

        invoice_response = self.create_invoice(
            record,
            [{"service": self.service.pk, "quantity": 2}],
        )
        self.assertEqual(invoice_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(invoice_response.data["patient"], patient.pk)
        self.assertEqual(invoice_response.data["medical_record"], record.pk)
        self.assertEqual(invoice_response.data["total_amount"], "500000.00")
        self.assertEqual(invoice_response.data["status"], Invoice.ISSUED)
        self.assertEqual(invoice_response.data["items"][0]["service"], self.service.pk)

        payment_response = self.receptionist_client.post(
            f"/api/v1/invoices/{invoice_response.data['id']}/pay-cash/",
            {"method": Payment.CASH},
            format="json",
        )
        self.assertEqual(payment_response.status_code, status.HTTP_200_OK)
        self.assertEqual(payment_response.data["status"], Invoice.PAID)
        self.assertEqual(payment_response.data["paid_amount"], "500000.00")
        self.assertEqual(payment_response.data["balance"], "0.00")
        self.assertEqual(len(payment_response.data["payments"]), 1)
        self.assertEqual(
            payment_response.data["payments"][0]["method"],
            Payment.CASH,
        )

        invoice = Invoice.objects.get(pk=invoice_response.data["id"])
        payment = Payment.objects.get(invoice=invoice)
        item = InvoiceItem.objects.get(invoice=invoice)
        appointment.refresh_from_db()
        self.assertEqual(invoice.patient_id, patient.pk)
        self.assertEqual(invoice.medical_record_id, record.pk)
        self.assertEqual(invoice.total_amount, Decimal("500000.00"))
        self.assertEqual(invoice.paid_amount, invoice.total_amount)
        self.assertEqual(item.service_id, self.service.pk)
        self.assertEqual(item.amount, Decimal("500000.00"))
        self.assertEqual(payment.amount, invoice.total_amount)
        self.assertEqual(payment.status, Payment.COMPLETED)
        self.assertEqual(payment.received_by_id, self.receptionist_profile.pk)
        self.assertEqual(appointment.patient_id, invoice.patient_id)

    def test_failed_steps_allow_retry_and_recover_through_qr_payment(self):
        patient = self.create_patient()
        invalid_appointment = self.receptionist_client.post(
            "/api/v1/appointments/",
            self.appointment_payload(
                patient,
                self.appointment_start + timedelta(minutes=45),
            ),
            format="json",
        )
        self.assertEqual(invalid_appointment.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Appointment.objects.exists())

        appointment = self.book_appointment(patient)
        invalid_record = self.dentist_client.post(
            "/api/v1/medical-records/",
            {"appointment": appointment.pk},
            format="json",
        )
        self.assertEqual(invalid_record.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(MedicalRecord.objects.exists())

        record = self.create_medical_record(appointment)
        with patch(
            "appointments.views.generate_medical_record_summary",
            side_effect=[AIServiceTimeoutError(), "Ghi nhận: sâu răng."],
        ) as generate_summary:
            failed_summary = self.dentist_client.post(
                f"/api/v1/medical-records/{record.pk}/ai-summary/",
                {},
                format="json",
            )
            retried_summary = self.dentist_client.post(
                f"/api/v1/medical-records/{record.pk}/ai-summary/",
                {},
                format="json",
            )
        self.assertEqual(failed_summary.status_code, status.HTTP_504_GATEWAY_TIMEOUT)
        self.assertEqual(failed_summary.data["code"], "ai_timeout")
        self.assertEqual(retried_summary.status_code, status.HTTP_200_OK)
        self.assertEqual(generate_summary.call_count, 2)

        with patch(
            "appointments.views.generate_generic_follow_up_text",
            side_effect=[AIServiceError("temporary generation failure"), "Vui lòng liên hệ phòng khám."],
        ) as generate_reminder:
            failed_reminder = self.receptionist_client.post(
                "/api/ai/generate-reminder",
                {"medical_record_id": record.pk},
                format="json",
            )
            retried_reminder = self.receptionist_client.post(
                "/api/ai/generate-reminder",
                {"medical_record_id": record.pk},
                format="json",
            )
        self.assertEqual(failed_reminder.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(retried_reminder.status_code, status.HTTP_200_OK)
        self.assertFalse(retried_reminder.data["sent"])
        self.assertEqual(generate_reminder.call_count, 2)
        self.assertFalse(FollowUpReminder.objects.filter(medical_record=record).exists())

        invalid_invoice = self.create_invoice(record, [])
        self.assertEqual(invalid_invoice.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Invoice.objects.exists())
        invoice_response = self.create_invoice(
            record,
            [{"service": self.service.pk, "quantity": 1}],
        )
        self.assertEqual(invoice_response.status_code, status.HTTP_201_CREATED)

        invoice_id = invoice_response.data["id"]
        qr_response = self.receptionist_client.post(
            f"/api/v1/invoices/{invoice_id}/pay-qr/",
            {},
            format="json",
        )
        self.assertEqual(qr_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(qr_response.data["invoice"]["status"], Invoice.ISSUED)
        self.assertEqual(qr_response.data["transfer"]["status"], Payment.PENDING)

        invalid_reconciliation = self.receptionist_client.post(
            f"/api/v1/invoices/{invoice_id}/reconcile-qr/",
            {
                "bank_reference": "WORKFLOW-BANK-TXN-001",
                "verified_amount": "1.00",
                "verified": True,
            },
            format="json",
        )
        self.assertEqual(
            invalid_reconciliation.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertFalse(BankTransferVerification.objects.exists())

        reconciliation = self.receptionist_client.post(
            f"/api/v1/invoices/{invoice_id}/reconcile-qr/",
            {
                "bank_reference": "WORKFLOW-BANK-TXN-001",
                "verified_amount": "250000.00",
                "verified": True,
            },
            format="json",
        )
        self.assertEqual(reconciliation.status_code, status.HTTP_200_OK)
        self.assertEqual(reconciliation.data["status"], Invoice.PAID)
        self.assertEqual(reconciliation.data["paid_amount"], "250000.00")

        invoice = Invoice.objects.get(pk=invoice_id)
        payment = Payment.objects.get(invoice=invoice)
        verification = BankTransferVerification.objects.get(payment=payment)
        self.assertEqual(invoice.medical_record_id, record.pk)
        self.assertEqual(invoice.patient_id, patient.pk)
        self.assertEqual(invoice.paid_amount, invoice.total_amount)
        self.assertEqual(payment.method, Payment.BANK_TRANSFER)
        self.assertEqual(payment.status, Payment.COMPLETED)
        self.assertEqual(verification.reference, "WORKFLOW-BANK-TXN-001")
        self.assertEqual(verification.verified_by_id, self.receptionist.pk)
        self.assertEqual(
            ActiveInvoicePayment.objects.get(invoice=invoice).payment_id,
            payment.pk,
        )
