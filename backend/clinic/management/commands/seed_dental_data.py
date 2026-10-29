import os
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from appointments.models import Appointment as ScheduledAppointment
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
    help = "Tạo tài khoản, bệnh nhân, dịch vụ, lịch hẹn và hóa đơn mẫu (có thể chạy lặp lại)"

    @transaction.atomic
    def handle(self, *args, **options):
        role_specs = [
            ("ADMIN", "Quản trị viên", "Quản trị hệ thống phòng khám"),
            ("DENTIST", "Bác sĩ", "Bác sĩ nha khoa"),
            ("RECEPTIONIST", "Lễ tân", "Tiếp đón và quản lý lịch hẹn"),
        ]
        roles = {
            code: Role.objects.update_or_create(code=code, defaults={"name": name, "description": description})[0]
            for code, name, description in role_specs
        }

        staff_specs = [
            ("admin", "DMS", "Quản trị viên", "ADMIN", "0901000001", ""),
            ("doctor1", "Lê Thu", "Hà", "DENTIST", "0901000002", "DMS-DOC-001"),
            ("doctor2", "Phạm", "Quốc", "DENTIST", "0901000003", "DMS-DOC-002"),
            ("receptionist1", "Nguyễn", "Lan", "RECEPTIONIST", "0901000004", ""),
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
                        "specialization": "Nha khoa tổng quát",
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
            ("DMS-0001", "Nguyễn Minh Anh", "0901234567", Patient.ADULT, "Penicillin"),
            ("DMS-0002", "Trần Gia Bảo", "0912345678", Patient.CHILD, ""),
            ("DMS-0003", "Lê Thu Phương", "0985552026", Patient.ADULT, ""),
            ("DMS-0004", "Phạm Đức Minh", "0971112233", Patient.ADULT, ""),
            ("DMS-0005", "Võ Khánh Linh", "0962223344", Patient.CHILD, ""),
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
            ("CONSULT", "Khám tư vấn nha khoa", Decimal("200000"), 30),
            ("CLEANING", "Cạo vôi và đánh bóng răng", Decimal("500000"), 45),
            ("FILLING", "Trám răng", Decimal("800000"), 60),
            ("EXTRACTION", "Nhổ răng đơn giản", Decimal("700000"), 45),
            ("XRAY", "Chụp X-quang răng", Decimal("150000"), 15),
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
                "dentist_name": "Bác sĩ Lê Thu Hà",
                "room": "Phòng 01",
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
        ScheduledAppointment.objects.get_or_create(
            patient=patients["DMS-0001"],
            doctor=staff["doctor1"].doctor_profile,
            appointment_date=start,
            defaults={
                "service": services["CLEANING"],
                "status": ScheduledAppointment.Status.CONFIRMED,
                "notes": "Lịch hẹn cạo vôi răng mẫu",
            },
        )

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
        plan, _ = TreatmentPlan.objects.get_or_create(
            patient=patients["DMS-0001"],
            title="Chăm sóc răng định kỳ",
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
                "Đã tạo dữ liệu mẫu: 3 vai trò, 1 quản trị viên, 2 bác sĩ, 1 lễ tân, "
                "5 bệnh nhân, 5 dịch vụ, 52 răng và các hồ sơ liên quan."
            )
        )
        if not User.objects.get(username="admin").has_usable_password():
            self.stdout.write(
                "Tài khoản quản trị mẫu chưa có mật khẩu sử dụng được. Hãy đặt DMS_SEED_ADMIN_PASSWORD "
                "trước khi tạo dữ liệu mẫu hoặc chạy `python manage.py changepassword admin`."
            )
