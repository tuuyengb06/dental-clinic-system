from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from appointments.models import Appointment as ScheduledAppointment
from appointments.models import MedicalRecord
from authentication.models import User
from clinic.models import (
    Appointment,
    Invoice,
    InvoiceItem,
    Patient,
    Payment,
    Service,
    Tooth,
    WorkSchedule,
)


class SeedDentalDataCommandTests(TestCase):
    def test_repeated_seed_keeps_demo_records_idempotent(self):
        with patch.dict("os.environ", {"DMS_SEED_ADMIN_PASSWORD": "test-demo-password"}):
            call_command("seed_dental_data", verbosity=0)
            first_counts = self._seeded_counts()

            call_command("seed_dental_data", verbosity=0)

        self.assertEqual(self._seeded_counts(), first_counts)
        self.assertTrue(User.objects.get(username="admin").has_usable_password())
        self.assertEqual(first_counts["patients"], 5)
        self.assertEqual(first_counts["services"], 5)
        self.assertTrue(Service.objects.get(code="FILLING").description)
        self.assertEqual(first_counts["appointments"], 1)
        self.assertEqual(first_counts["scheduled_appointments"], 1)
        self.assertEqual(first_counts["medical_records"], 1)
        self.assertEqual(first_counts["invoices"], 2)
        self.assertEqual(first_counts["invoice_items"], 2)
        self.assertEqual(first_counts["payments"], 1)
        self.assertTrue(
            Invoice.objects.get(invoice_number="INV-0001").medical_record_id
        )
        self.assertEqual(
            Invoice.objects.get(invoice_number="INV-0002").payments.get().status,
            Payment.COMPLETED,
        )
        self.assertEqual(first_counts["teeth"], 52)
        self.assertEqual(first_counts["work_schedules"], 1)

    @staticmethod
    def _seeded_counts():
        return {
            "patients": Patient.objects.count(),
            "services": Service.objects.count(),
            "appointments": Appointment.objects.count(),
            "scheduled_appointments": ScheduledAppointment.objects.count(),
            "medical_records": MedicalRecord.objects.count(),
            "invoices": Invoice.objects.count(),
            "invoice_items": InvoiceItem.objects.count(),
            "payments": Payment.objects.count(),
            "teeth": Tooth.objects.count(),
            "work_schedules": WorkSchedule.objects.count(),
        }
