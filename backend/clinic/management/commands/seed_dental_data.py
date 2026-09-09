from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from clinic.models import Appointment, Invoice, Patient, Tooth


class Command(BaseCommand):
    help = "Seed DMS demo users, teeth, patients, appointments and invoices"

    def handle(self, *args, **options):
        for index in range(1, 33):
            Tooth.objects.get_or_create(code=f"A{index:02}", dentition_type=Patient.ADULT, defaults={"display_order": index})
        for index in range(1, 21):
            Tooth.objects.get_or_create(code=f"C{index:02}", dentition_type=Patient.CHILD, defaults={"display_order": index})
        adult, _ = Patient.objects.get_or_create(patient_code="DMS-0001", defaults={"full_name": "Nguyen Minh Anh", "phone": "0901234567", "dentition_type": Patient.ADULT, "allergies": "Penicillin"})
        child, _ = Patient.objects.get_or_create(patient_code="DMS-0002", defaults={"full_name": "Tran Gia Bao", "phone": "0912345678", "dentition_type": Patient.CHILD})
        start = timezone.now() + timedelta(hours=2)
        Appointment.objects.get_or_create(patient=adult, start_at=start, defaults={"dentist_name": "Dr. Le Thu Ha", "room": "Room 01", "end_at": start + timedelta(minutes=45), "status": Appointment.CONFIRMED})
        Invoice.objects.get_or_create(patient=adult, invoice_number="INV-0001", defaults={"total_amount": Decimal("3500000"), "status": Invoice.ISSUED})
        self.stdout.write(self.style.SUCCESS("Seeded 32 adult teeth, 20 child teeth and demo clinic data."))
