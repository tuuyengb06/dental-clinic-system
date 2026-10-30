import uuid
from collections.abc import Mapping
from decimal import Decimal
from pathlib import Path, PureWindowsPath

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from appointments.models import MedicalRecord
from .models import (
    BankTransferVerification,
    Doctor,
    Invoice,
    InvoiceItem,
    Patient,
    Payment,
    Radiograph,
    Service,
    Tooth,
    ToothCondition,
    TreatmentItem,
    TreatmentPlan,
    WorkSchedule,
)

class DoctorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    username = serializers.CharField(source="clinic_user.user.username", read_only=True)
    phone = serializers.CharField(source="clinic_user.phone", read_only=True)
    role = serializers.CharField(source="clinic_user.role.code", read_only=True)

    class Meta:
        model = Doctor
        fields = ["id", "full_name", "username", "license_number", "specialization", "experience_years", "phone", "role"]

    def get_full_name(self, doctor):
        user = doctor.clinic_user.user
        return user.get_full_name() or user.username

class WorkScheduleSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.__str__', read_only=True)

    class Meta:
        model = WorkSchedule
        fields = '__all__'

    def validate(self, attrs):
        start_time = attrs.get("start_time", self.instance.start_time if self.instance else None)
        end_time = attrs.get("end_time", self.instance.end_time if self.instance else None)
        doctor = attrs.get("doctor", self.instance.doctor if self.instance else None)
        work_date = attrs.get("work_date", self.instance.work_date if self.instance else None)
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({"end_time": "End time must be later than start time."})
        if doctor and work_date and start_time and end_time:
            overlapping = WorkSchedule.objects.filter(
                doctor=doctor,
                work_date=work_date,
                start_time__lt=end_time,
                end_time__gt=start_time,
            )
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            if overlapping.exists():
                raise serializers.ValidationError("This shift overlaps another work shift.")
        return attrs

class DentalServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service  # Dùng đúng tên Service từ models.py
        fields = '__all__'


class PatientSerializer(serializers.ModelSerializer):
    has_login_account = serializers.SerializerMethodField()
    login_username = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            "id", "patient_code", "full_name", "phone", "date_of_birth",
            "dentition_type", "medical_history", "allergies",
            "ai_processing_consent", "sms_reminder_consent", "created_at",
            "has_login_account", "login_username",
        ]
        read_only_fields = ["id", "created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        user = getattr(request, "user", None)
        clinic_profile = getattr(user, "clinic_profile", None)
        if not user or not (
            user.is_superuser
            or (clinic_profile and clinic_profile.role.code == "ADMIN")
        ):
            self.fields.pop("has_login_account", None)
            self.fields.pop("login_username", None)

    def get_has_login_account(self, patient):
        return bool(patient.user_id)

    def get_login_username(self, patient):
        return patient.user.username if patient.user_id else None

    def validate(self, attrs):
        phone = attrs.get("phone", getattr(self.instance, "phone", ""))
        sms_consent = attrs.get(
            "sms_reminder_consent",
            getattr(self.instance, "sms_reminder_consent", False),
        )
        if sms_consent and not phone.strip():
            raise serializers.ValidationError(
                {"sms_reminder_consent": "A phone number is required for SMS reminders."}
            )
        return attrs


class ToothSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tooth
        fields = ["id", "code", "dentition_type", "display_order"]


class RadiographSerializer(serializers.ModelSerializer):
    image = serializers.FileField(write_only=True)

    class Meta:
        model = Radiograph
        fields = [
            "id",
            "patient",
            "image",
            "original_filename",
            "content_type",
            "file_size",
            "uploaded_at",
        ]
        read_only_fields = [
            "id",
            "original_filename",
            "content_type",
            "file_size",
            "uploaded_at",
        ]

    def validate_image(self, uploaded):
        if uploaded.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Ảnh X-quang không được vượt quá 10 MB.")
        if uploaded.size < 12:
            raise serializers.ValidationError("Tệp ảnh quá ngắn hoặc không hợp lệ.")

        windows_name = PureWindowsPath(uploaded.name).name
        filename = Path(windows_name).name
        extension = Path(filename).suffix.lower()
        if extension not in {".jpg", ".jpeg", ".png"}:
            raise serializers.ValidationError("Chỉ chấp nhận ảnh JPG, JPEG hoặc PNG.")

        signature = uploaded.read(8)
        uploaded.seek(0)
        if signature.startswith(b"\x89PNG\r\n\x1a\n"):
            detected_type = "image/png"
        elif signature.startswith(b"\xff\xd8\xff"):
            detected_type = "image/jpeg"
        else:
            raise serializers.ValidationError("Tệp tải lên không phải ảnh PNG hoặc JPEG hợp lệ.")

        if extension == ".png" and detected_type != "image/png":
            raise serializers.ValidationError("Phần mở rộng tệp không khớp định dạng ảnh.")
        if extension in {".jpg", ".jpeg"} and detected_type != "image/jpeg":
            raise serializers.ValidationError("Phần mở rộng tệp không khớp định dạng ảnh.")
        uploaded._radiograph_content_type = detected_type
        uploaded._radiograph_original_filename = filename
        return uploaded

    def create(self, validated_data):
        image = validated_data["image"]
        return Radiograph.objects.create(
            **validated_data,
            original_filename=image._radiograph_original_filename,
            content_type=image._radiograph_content_type,
            file_size=image.size,
            uploaded_by=self.context["request"].user.clinic_profile,
        )


class ToothConditionSerializer(serializers.ModelSerializer):
    tooth_code = serializers.CharField(source="tooth.code", read_only=True)
    condition = serializers.ChoiceField(
        choices=("Healthy", "Needs care", "Monitor", "Restored")
    )

    class Meta:
        model = ToothCondition
        fields = ["id", "patient", "tooth", "tooth_code", "condition", "note", "updated_at"]
        read_only_fields = ["id", "tooth_code", "updated_at"]
        validators = []

    def validate(self, attrs):
        patient = attrs.get("patient", self.instance.patient if self.instance else None)
        tooth = attrs.get("tooth", self.instance.tooth if self.instance else None)
        if patient and tooth and patient.dentition_type != tooth.dentition_type:
            raise serializers.ValidationError(
                {"tooth": "The selected tooth does not match the patient's dentition."}
            )
        return attrs


class TreatmentItemSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True, allow_null=True)
    tooth_code = serializers.CharField(source="tooth.code", read_only=True, allow_null=True)

    class Meta:
        model = TreatmentItem
        fields = [
            "id", "plan", "appointment", "service", "service_name", "procedure_name",
            "tooth", "tooth_code", "cost", "status",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        plan = attrs.get("plan", self.instance.plan if self.instance else None)
        tooth = attrs.get("tooth", self.instance.tooth if self.instance else None)
        appointment = attrs.get(
            "appointment", self.instance.appointment if self.instance else None
        )
        if plan and tooth and tooth.dentition_type != plan.patient.dentition_type:
            raise serializers.ValidationError(
                {"tooth": "Răng được chọn không khớp với bộ răng của bệnh nhân."}
            )
        if appointment and plan and (
            appointment.patient_id != plan.patient_id
            or appointment.doctor_id != plan.dentist_id
        ):
            raise serializers.ValidationError(
                {"appointment": "Lịch khám phải thuộc đúng bệnh nhân và bác sĩ điều trị."}
            )
        request = self.context.get("request")
        user = getattr(request, "user", None)
        clinic_profile = getattr(user, "clinic_profile", None)
        if plan and clinic_profile and clinic_profile.role.code == "DENTIST":
            if plan.dentist_id != getattr(
                getattr(clinic_profile, "doctor_profile", None), "id", None
            ):
                raise serializers.ValidationError(
                    {"plan": "Bạn chỉ được cập nhật kế hoạch điều trị của mình."}
                )
        return attrs


class TreatmentPlanSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    dentist_name = serializers.SerializerMethodField()
    items = TreatmentItemSerializer(many=True, read_only=True)

    class Meta:
        model = TreatmentPlan
        fields = [
            "id", "patient", "patient_name", "dentist", "dentist_name", "title",
            "status", "start_date", "end_date", "created_at", "items",
        ]
        read_only_fields = ["id", "created_at"]

    def get_dentist_name(self, plan):
        user = plan.dentist.clinic_user.user
        return user.get_full_name() or user.username

    def validate(self, attrs):
        dentist = attrs.get("dentist", self.instance.dentist if self.instance else None)
        patient = attrs.get("patient", self.instance.patient if self.instance else None)
        start_date = attrs.get("start_date", self.instance.start_date if self.instance else None)
        end_date = attrs.get("end_date", self.instance.end_date if self.instance else None)
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": "Ngày kết thúc không được trước ngày bắt đầu."}
            )
        request = self.context.get("request")
        clinic_profile = getattr(getattr(request, "user", None), "clinic_profile", None)
        if clinic_profile and clinic_profile.role.code == "DENTIST":
            assigned_doctor = getattr(clinic_profile, "doctor_profile", None)
            if not assigned_doctor or dentist != assigned_doctor:
                raise serializers.ValidationError(
                    {"dentist": "Bác sĩ chỉ được lập kế hoạch điều trị cho chính mình."}
                )
            from appointments.models import Appointment

            if patient and not Appointment.objects.filter(
                patient=patient, doctor=assigned_doctor
            ).exists():
                raise serializers.ValidationError(
                    {"patient": "Bệnh nhân chưa có lịch khám được phân công cho bác sĩ."}
                )
        return attrs


class InvoiceItemSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True, allow_null=True)

    class Meta:
        model = InvoiceItem
        fields = ["id", "service", "service_name", "description", "quantity", "unit_price", "amount"]
        read_only_fields = fields


class PaymentSerializer(serializers.ModelSerializer):
    received_by_name = serializers.SerializerMethodField()
    bank_reference = serializers.SerializerMethodField()
    verified_at = serializers.SerializerMethodField()
    verified_by_name = serializers.SerializerMethodField()
    cancelled_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id",
            "amount",
            "method",
            "status",
            "created_at",
            "paid_at",
            "received_by_name",
            "bank_reference",
            "verified_at",
            "verified_by_name",
            "cancelled_at",
            "cancelled_by_name",
        ]
        read_only_fields = fields

    def get_received_by_name(self, payment):
        clinic_user = payment.received_by
        if not clinic_user:
            return None
        user = clinic_user.user
        return user.get_full_name() or user.username

    def get_verified_by_name(self, payment):
        try:
            user = payment.verification.verified_by
        except BankTransferVerification.DoesNotExist:
            return None
        return user.get_full_name() or user.username

    def get_cancelled_by_name(self, payment):
        user = payment.cancelled_by
        if not user:
            return None
        return user.get_full_name() or user.username

    def get_bank_reference(self, payment):
        try:
            return payment.verification.reference
        except BankTransferVerification.DoesNotExist:
            return None

    def get_verified_at(self, payment):
        try:
            return payment.verification.verified_at
        except BankTransferVerification.DoesNotExist:
            return None


class ManualQrReconciliationSerializer(serializers.Serializer):
    bank_reference = serializers.CharField(max_length=100, allow_blank=False, trim_whitespace=True)
    verified_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    verified = serializers.BooleanField()

    def validate_bank_reference(self, value):
        if not value:
            raise serializers.ValidationError("Enter the transaction reference shown by the bank.")
        return value

    def to_internal_value(self, data):
        if isinstance(data, Mapping) and set(data) - set(self.fields):
            raise serializers.ValidationError(
                {"detail": "Only bank_reference, verified_amount, and verified are accepted."}
            )
        return super().to_internal_value(data)

    def validate_verified(self, value):
        if not value:
            raise serializers.ValidationError(
                "Confirm that the bank statement was checked before recording the transfer."
            )
        return value


class CancelQrPaymentSerializer(serializers.Serializer):
    checked_no_payment = serializers.BooleanField()

    def to_internal_value(self, data):
        if isinstance(data, Mapping) and set(data) - set(self.fields):
            raise serializers.ValidationError(
                {"detail": "Only checked_no_payment is accepted."}
            )
        return super().to_internal_value(data)

    def validate_checked_no_payment(self, value):
        if not value:
            raise serializers.ValidationError(
                "Confirm that the receiving account was checked and no transfer was received."
            )
        return value


class InvoiceServiceSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["id", "name", "price"]


class InvoiceSourceSerializer(serializers.ModelSerializer):
    appointment = serializers.IntegerField(source="appointment_id", read_only=True)
    appointment_date = serializers.DateTimeField(source="appointment.appointment_date", read_only=True)
    patient = serializers.IntegerField(source="appointment.patient_id", read_only=True)
    patient_name = serializers.CharField(source="appointment.patient.full_name", read_only=True)
    patient_code = serializers.CharField(source="appointment.patient.patient_code", read_only=True)
    services = InvoiceServiceSourceSerializer(many=True, read_only=True)

    class Meta:
        model = MedicalRecord
        fields = ["id", "appointment", "appointment_date", "patient", "patient_name", "patient_code", "services"]


class InvoiceItemInputSerializer(serializers.Serializer):
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())
    quantity = serializers.IntegerField(min_value=1, max_value=32767)


class InvoiceCreateSerializer(serializers.Serializer):
    medical_record = serializers.PrimaryKeyRelatedField(queryset=MedicalRecord.objects.all())
    items = InvoiceItemInputSerializer(many=True)

    def validate(self, attrs):
        medical_record = attrs["medical_record"]
        requested_items = attrs["items"]
        requested_ids = [item["service"].id for item in requested_items]
        if len(requested_ids) != len(set(requested_ids)):
            raise serializers.ValidationError({"items": "Each prescribed service may appear only once."})

        prescribed_services = {
            service.id: service for service in medical_record.services.all()
        }
        if not prescribed_services:
            raise serializers.ValidationError(
                {"medical_record": "This examination record has no prescribed services to invoice."}
            )
        if set(requested_ids) != set(prescribed_services):
            raise serializers.ValidationError(
                {"items": "Include every service prescribed on the examination record exactly once."}
            )
        if Invoice.objects.filter(medical_record=medical_record).exists():
            raise serializers.ValidationError(
                {"medical_record": "An invoice already exists for this examination record."}
            )

        maximum_amount = Decimal("9999999999.99")
        total = Decimal("0")
        for item in requested_items:
            unit_price = item["service"].price
            line_total = unit_price * item["quantity"]
            if unit_price < 0 or line_total > maximum_amount:
                raise serializers.ValidationError(
                    {"items": "A service price or line total is outside the supported range."}
                )
            total += line_total
        if total > maximum_amount:
            raise serializers.ValidationError(
                {"items": "The invoice total is outside the supported range."}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        medical_record = MedicalRecord.objects.select_for_update().select_related(
            "appointment__patient"
        ).get(pk=validated_data["medical_record"].pk)
        prescribed_services = {
            service.id: service for service in medical_record.services.all()
        }
        requested_items = validated_data["items"]
        requested_ids = [item["service"].id for item in requested_items]
        if (
            len(requested_ids) != len(set(requested_ids))
            or set(requested_ids) != set(prescribed_services)
        ):
            raise serializers.ValidationError(
                {"items": "The prescribed services changed. Reload the examination record and try again."}
            )

        maximum_amount = Decimal("9999999999.99")
        total = Decimal("0")
        invoice_items = []
        for item in requested_items:
            service = prescribed_services[item["service"].id]
            line_total = service.price * item["quantity"]
            if service.price < 0 or line_total > maximum_amount:
                raise serializers.ValidationError(
                    {"items": "A service price or line total is outside the supported range."}
                )
            total += line_total
            invoice_items.append((service, item["quantity"], line_total))
        if total > maximum_amount:
            raise serializers.ValidationError(
                {"items": "The invoice total is outside the supported range."}
            )

        invoice = Invoice.objects.create(
            medical_record=medical_record,
            patient=medical_record.appointment.patient,
            invoice_number=f"INV-{timezone.localdate():%Y%m%d}-{uuid.uuid4().hex[:8].upper()}",
            total_amount=Decimal("0"),
            paid_amount=Decimal("0"),
            status=Invoice.ISSUED,
        )
        for service, quantity, line_total in invoice_items:
            InvoiceItem.objects.create(
                invoice=invoice,
                service=service,
                description=service.name,
                quantity=quantity,
                unit_price=service.price,
                amount=line_total,
            )
        invoice.total_amount = total
        invoice.save(update_fields=["total_amount"])
        return invoice


class CashPaymentRequestSerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=[Payment.CASH])

    def to_internal_value(self, data):
        if isinstance(data, Mapping) and set(data) - set(self.fields):
            raise serializers.ValidationError(
                {"non_field_errors": "Payment amount and invoice totals are calculated by the server."}
            )
        return super().to_internal_value(data)


class InvoiceSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    medical_record = serializers.IntegerField(source="medical_record_id", read_only=True, allow_null=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id", "patient", "patient_name", "medical_record", "invoice_number",
            "total_amount", "paid_amount", "balance", "status", "issued_at", "items",
            "payments",
        ]
        read_only_fields = fields