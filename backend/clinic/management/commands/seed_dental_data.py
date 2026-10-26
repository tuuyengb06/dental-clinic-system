import os
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from appointments.models import (
    Appointment as ScheduledAppointment,
    MedicalRecord,
)
from clinic.models import (
    Appointment,
    ClinicUser,
    Doctor,
    Invoice,
    InvoiceItem,
    Patient,
    Payment,
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
            ("admin", "DMS", "Administrator", "ADMIN", "0901000001", ""),
            ("doctor1", "Le Thu", "Ha", "DENTIST", "0901000002", "DMS-DOC-001"),
            ("doctor2", "Pham", "Quoc", "DENTIST", "0901000003", "DMS-DOC-002"),
            ("receptionist1", "Nguyen", "Lan", "RECEPTIONIST", "0901000004", ""),
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
            if created or (role_code == "ADMIN" and admin_password):
                if role_code == "ADMIN" and admin_password:
                    user.set_password(admin_password)
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
            ("DMS-0001", "Nguyen Minh Anh", "0901234567", Patient.ADULT, "Penicillin"),
            ("DMS-0002", "Tran Gia Bao", "0912345678", Patient.CHILD, ""),
            ("DMS-0003", "Le Thu Phuong", "0985552026", Patient.ADULT, ""),
            ("DMS-0004", "Pham Duc Minh", "0971112233", Patient.ADULT, ""),
            ("DMS-0005", "Vo Khanh Linh", "0962223344", Patient.CHILD, ""),
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
                },
            )

        service_specs = [
            (
                "CONSULT",
                "Dental consultation",
                "Bác sĩ kiểm tra tình trạng răng miệng và trao đổi với bệnh nhân về nhu cầu khám.",
                Decimal("200000"),
                30,
            ),
            (
                "CLEANING",
                "Scaling and polishing",
                "Làm sạch cao răng và đánh bóng bề mặt răng theo chỉ định của bác sĩ.",
                Decimal("500000"),
                45,
            ),
            (
                "FILLING",
                "Tooth filling",
                "Sử dụng vật liệu nha khoa để phục hồi phần răng bị tổn thương phù hợp với đánh giá của bác sĩ.",
                Decimal("800000"),
                60,
            ),
            (
                "EXTRACTION",
                "Simple extraction",
                "Thủ thuật lấy răng được bác sĩ đánh giá là có thể nhổ đơn giản.",
                Decimal("700000"),
                45,
            ),
            (
                "XRAY",
                "Dental X-ray",
                "Chụp hình ảnh X-quang răng để hỗ trợ bác sĩ kiểm tra cấu trúc răng và vùng liên quan.",
                Decimal("150000"),
                15,
            ),
        ]
        services = {}
        for code, name, description, price, duration in service_specs:
            services[code], _ = Service.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": description,
                    "price": price,
                    "duration_minutes": duration,
                    "is_active": True,
                },
            )

        appointment = Appointment.objects.filter(
            patient=patients["DMS-0001"],
            notes="Seeded demo appointment",
        ).order_by("id").first()
        if appointment is None:
            start = timezone.localtime().replace(
                hour=9,
                minute=0,
                second=0,
                microsecond=0,
            )
            if start <= timezone.localtime():
                start += timedelta(days=1)
            appointment = Appointment.objects.create(
                patient=patients["DMS-0001"],
                doctor=staff["doctor1"].doctor_profile,
                dentist_name="Dr. Le Thu Ha",
                room="Room 01",
                start_at=start,
                end_at=start + timedelta(minutes=45),
                status=Appointment.CONFIRMED,
                notes="Seeded demo appointment",
            )
        local_appointment_start = timezone.localtime(appointment.start_at)
        WorkSchedule.objects.get_or_create(
            doctor=staff["doctor1"].doctor_profile,
            work_date=local_appointment_start.date(),
            start_time=local_appointment_start.time(),
            end_time=local_appointment_start.replace(hour=17).time(),
        )
        scheduled_appointment = ScheduledAppointment.objects.filter(
            patient=patients["DMS-0001"],
            doctor=staff["doctor1"].doctor_profile,
            notes="Seeded cleaning appointment",
        ).order_by("id").first()
        if scheduled_appointment is None:
            ScheduledAppointment.objects.create(
                patient=patients["DMS-0001"],
                doctor=staff["doctor1"].doctor_profile,
                appointment_date=appointment.start_at,
                service=services["CLEANING"],
                status=ScheduledAppointment.Status.CONFIRMED,
                notes="Seeded cleaning appointment",
            )
            scheduled_appointment = ScheduledAppointment.objects.get(
                patient=patients["DMS-0001"],
                doctor=staff["doctor1"].doctor_profile,
                notes="Seeded cleaning appointment",
            )
        medical_record, _ = MedicalRecord.objects.get_or_create(
            appointment=scheduled_appointment,
            defaults={
                "diagnosis": "Routine dental check-up",
                "treatment_plan": "Scaling and polishing",
                "prescription": "",
                "notes": "Seeded demo medical record",
                "follow_up_date": date.today() + timedelta(days=180),
            },
        )
        medical_record.services.add(services["CLEANING"])

        invoice, _ = Invoice.objects.update_or_create(
            patient=patients["DMS-0001"],
            invoice_number="INV-0001",
            defaults={
                "medical_record": medical_record,
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
        paid_invoice, _ = Invoice.objects.update_or_create(
            patient=patients["DMS-0003"],
            invoice_number="INV-0002",
            defaults={
                "total_amount": services["CONSULT"].price,
                "paid_amount": services["CONSULT"].price,
                "status": Invoice.PAID,
            },
        )
        InvoiceItem.objects.get_or_create(
            invoice=paid_invoice,
            service=services["CONSULT"],
            defaults={
                "description": services["CONSULT"].name,
                "quantity": 1,
                "unit_price": services["CONSULT"].price,
            },
        )
        if not Payment.objects.filter(
            invoice=paid_invoice,
            status=Payment.COMPLETED,
        ).exists():
            Payment.objects.create(
                invoice=paid_invoice,
                amount=paid_invoice.total_amount,
                method=Payment.CASH,
                status=Payment.COMPLETED,
                paid_at=timezone.now(),
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
                "5 patients, 5 services, 52 teeth, 1 medical record, 2 invoices, "
                "1 payment, and related demo records."
            )
        )
        if not User.objects.get(username="admin").has_usable_password():
            self.stdout.write(
                "The seeded admin has no usable password. Set DMS_SEED_ADMIN_PASSWORD before seeding, "
                "or run `python manage.py changepassword admin`."
            )
