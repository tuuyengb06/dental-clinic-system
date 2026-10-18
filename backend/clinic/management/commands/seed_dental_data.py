import os
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils import timezone

from appointments.models import (
    Appointment as ScheduledAppointment,
    MedicalRecord as ScheduledMedicalRecord,
)
from clinic.models import (
    Appointment,
    ClinicUser,
    Doctor,
    Invoice,
    InvoiceItem,
    Patient,
    Role,
    Service,
    Tooth,
    TreatmentItem,
    TreatmentPlan,
    WorkSchedule,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Create idempotent demo accounts, patients, services, appointments and invoices"

    @transaction.atomic
    def handle(self, *args, **options):
        demo_password = os.environ.get("DMS_SEED_DEMO_PASSWORD", "")
        if demo_password:
            validate_password(demo_password)

        role_specs = [
            ("ADMIN", "Administrator", "Clinic system administrator"),
            ("DENTIST", "Dentist", "Dental care provider"),
            ("RECEPTIONIST", "Receptionist", "Front desk and appointment management"),
        ]
        roles = {
            code: Role.objects.update_or_create(code=code, defaults={"name": name, "description": description})[0]
            for code, name, description in role_specs
        }

        staff_specs = [
            ("admin", "DMS", "Administrator", "ADMIN", "0000000000", ""),
            ("doctor1", "Le Thu", "Ha", "DENTIST", "0000000000", "DMS-DOC-001"),
            ("doctor2", "Pham", "Quoc", "DENTIST", "0000000000", "DMS-DOC-002"),
            ("receptionist1", "Nguyen", "Lan", "RECEPTIONIST", "0000000000", ""),
        ]
        staff = {}
        admin_password = os.environ.get("DMS_SEED_ADMIN_PASSWORD")
        legacy_admin = User.objects.filter(username="dms_admin").first()
        if legacy_admin and not User.objects.filter(username="admin").exists():
            legacy_admin.username = "admin"
            legacy_admin.save(update_fields=["username"])

        for username, first_name, last_name, role_code, phone, license_number in staff_specs:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_staff": role_code == "ADMIN",
                    "is_superuser": role_code == "ADMIN",
                },
            )
            if created or demo_password or (role_code == "ADMIN" and admin_password):
                if role_code == "ADMIN" and admin_password:
                    user.set_password(admin_password)
                elif demo_password:
                    user.set_password(demo_password)
                else:
                    user.set_unusable_password()
                user.save(update_fields=["password"])
            clinic_user, _ = ClinicUser.objects.update_or_create(
                user=user,
                defaults={"role": roles[role_code], "phone": phone},
            )
            staff[username] = clinic_user
            if license_number:
                Doctor.objects.update_or_create(
                    clinic_user=clinic_user,
                    defaults={
                        "license_number": license_number,
                        "specialization": "General dentistry",
                    },
                )

        for index in range(1, 33):
            Tooth.objects.get_or_create(
                code=f"A{index:02}",
                dentition_type=Patient.ADULT,
                defaults={"display_order": index},
            )
        for index in range(1, 21):
            Tooth.objects.get_or_create(
                code=f"C{index:02}",
                dentition_type=Patient.CHILD,
                defaults={"display_order": index},
            )

        patient_specs = [
            ("DMS-0001", "Synthetic Demo Patient One", "0000000000", Patient.ADULT, "Penicillin"),
            ("DMS-0002", "Synthetic Demo Patient Two", "0000000000", Patient.CHILD, ""),
            ("DMS-0003", "Synthetic Demo Patient Three", "0000000000", Patient.ADULT, ""),
            ("DMS-0004", "Synthetic Demo Patient Four", "0000000000", Patient.ADULT, ""),
            ("DMS-0005", "Synthetic Demo Patient Five", "0000000000", Patient.CHILD, ""),
        ]
        patients = {}
        for code, name, phone, dentition, allergies in patient_specs:
            patients[code], _ = Patient.objects.update_or_create(
                patient_code=code,
                defaults={
                    "full_name": name,
                    "phone": phone,
                    "dentition_type": dentition,
                    "allergies": allergies,
                    "ai_processing_consent": False,
                    "sms_reminder_consent": False,
                },
            )

        service_specs = [
            ("CONSULT", "Dental consultation", Decimal("200000"), 30),
            ("CLEANING", "Scaling and polishing", Decimal("500000"), 45),
            ("FILLING", "Tooth filling", Decimal("800000"), 60),
            ("EXTRACTION", "Simple extraction", Decimal("700000"), 45),
            ("XRAY", "Dental X-ray", Decimal("150000"), 15),
        ]
        services = {}
        for code, name, price, duration in service_specs:
            services[code], _ = Service.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "price": price,
                    "duration_minutes": duration,
                    "is_active": True,
                },
            )

        start = timezone.localtime().replace(hour=9, minute=0, second=0, microsecond=0)
        if start <= timezone.localtime():
            start += timedelta(days=1)
        appointment, _ = Appointment.objects.get_or_create(
            patient=patients["DMS-0001"],
            start_at=start,
            defaults={
                "doctor": staff["doctor1"].doctor_profile,
                "dentist_name": "Dr. Le Thu Ha",
                "room": "Room 01",
                "end_at": start + timedelta(minutes=45),
                "status": Appointment.CONFIRMED,
            },
        )
        WorkSchedule.objects.get_or_create(
            doctor=staff["doctor1"].doctor_profile,
            work_date=start.date(),
            start_time=start.time(),
            end_time=start.replace(hour=17).time(),
        )
        scheduled_appointment, _ = ScheduledAppointment.objects.get_or_create(
            patient=patients["DMS-0001"],
            doctor=staff["doctor1"].doctor_profile,
            appointment_date=start,
            defaults={
                "service": services["CLEANING"],
                "status": ScheduledAppointment.Status.CONFIRMED,
                "notes": "Seeded cleaning appointment",
            },
        )
        completed_start = start - timedelta(days=1)
        WorkSchedule.objects.get_or_create(
            doctor=staff["doctor1"].doctor_profile,
            work_date=completed_start.date(),
            start_time=completed_start.time(),
            end_time=completed_start.replace(hour=17).time(),
        )
        completed_appointment, _ = ScheduledAppointment.objects.get_or_create(
            patient=patients["DMS-0001"],
            doctor=staff["doctor1"].doctor_profile,
            appointment_date=completed_start,
            defaults={
                "service": services["CLEANING"],
                "status": ScheduledAppointment.Status.COMPLETED,
                "notes": "Synthetic demo appointment",
            },
        )
        medical_record, _ = ScheduledMedicalRecord.objects.update_or_create(
            appointment=completed_appointment,
            defaults={
                "diagnosis": "Synthetic demo record: mild plaque accumulation.",
                "treatment_plan": "Demonstration only: routine scaling and polishing.",
                "prescription": "",
                "notes": "Fictional training data. Not a real patient record.",
                "follow_up_date": timezone.localdate() + timedelta(days=7),
            },
        )
        medical_record.services.set([services["CLEANING"]])

        invoice, _ = Invoice.objects.update_or_create(
            patient=patients["DMS-0001"],
            invoice_number="INV-0001",
            defaults={
                "total_amount": services["CLEANING"].price,
                "status": Invoice.ISSUED,
            },
        )
        InvoiceItem.objects.get_or_create(
            invoice=invoice,
            service=services["CLEANING"],
            defaults={
                "description": services["CLEANING"].name,
                "quantity": 1,
                "unit_price": Decimal("500000"),
            },
        )
        demo_invoice, invoice_created = Invoice.objects.get_or_create(
            medical_record=medical_record,
            defaults={
                "patient": patients["DMS-0001"],
                "invoice_number": "DEMO-INV-001",
                "total_amount": services["CLEANING"].price,
                "paid_amount": Decimal("0"),
                "status": Invoice.ISSUED,
            },
        )
        if invoice_created or not demo_invoice.payments.exists():
            demo_invoice.patient = patients["DMS-0001"]
            demo_invoice.invoice_number = "DEMO-INV-001"
            demo_invoice.total_amount = services["CLEANING"].price
            demo_invoice.paid_amount = Decimal("0")
            demo_invoice.status = Invoice.ISSUED
            demo_invoice.save(
                update_fields=[
                    "patient",
                    "invoice_number",
                    "total_amount",
                    "paid_amount",
                    "status",
                ]
            )
            InvoiceItem.objects.update_or_create(
                invoice=demo_invoice,
                service=services["CLEANING"],
                defaults={
                    "description": services["CLEANING"].name,
                    "quantity": 1,
                    "unit_price": services["CLEANING"].price,
                },
            )
        plan, _ = TreatmentPlan.objects.get_or_create(
            patient=patients["DMS-0001"],
            title="Routine dental care",
            defaults={
                "dentist": staff["doctor1"].doctor_profile,
                "status": TreatmentPlan.ACTIVE,
                "start_date": date.today(),
            },
        )
        TreatmentItem.objects.get_or_create(
            plan=plan,
            procedure_name=services["CLEANING"].name,
            defaults={
                "appointment": appointment,
                "service": services["CLEANING"],
                "cost": services["CLEANING"].price,
                "status": TreatmentItem.PLANNED,
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Seed complete: 3 roles, 1 admin, 2 dentists, 1 receptionist, "
                "5 synthetic patients, 5 services, 52 teeth, and linked appointment, "
                "medical-record, treatment, and invoice demo records."
            )
        )
        if not demo_password and not User.objects.get(username="admin").has_usable_password():
            self.stdout.write(
                "The seeded admin has no usable password. Set DMS_SEED_ADMIN_PASSWORD before seeding, "
                "or run `python manage.py changepassword admin`."
            )
        if not demo_password:
            self.stdout.write(
                "Demo accounts have no usable password by default. Set DMS_SEED_DEMO_PASSWORD "
                "to a strong local-only password before seeding, or set each password with "
                "`python manage.py changepassword <username>`."
            )
