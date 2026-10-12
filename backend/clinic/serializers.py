from rest_framework import serializers
from .models import Doctor, Patient, Tooth, WorkSchedule, Service, Invoice

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
    class Meta:
        model = Patient
        fields = [
            "id", "patient_code", "full_name", "phone", "date_of_birth",
            "dentition_type", "medical_history", "allergies", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ToothSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tooth
        fields = ["id", "code", "dentition_type", "display_order"]


class InvoiceSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id", "patient", "invoice_number", "total_amount", "paid_amount",
            "balance", "status", "issued_at",
        ]
        read_only_fields = ["id", "issued_at"]