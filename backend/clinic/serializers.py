from rest_framework import serializers
from .models import Appointment, ClinicUser, Doctor, Invoice, Patient, Service, Tooth, ToothCondition


class ClinicUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    display_name = serializers.SerializerMethodField()
    role = serializers.CharField(source="role.code", read_only=True)

    class Meta:
        model = ClinicUser
        fields = ["id", "username", "display_name", "role", "phone"]

    def get_display_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["id", "code", "name", "description", "price", "duration_minutes", "is_active"]


class DoctorDirectorySerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    phone = serializers.CharField(source="clinic_user.phone", read_only=True)
    role = serializers.CharField(source="clinic_user.role.name", read_only=True)

    class Meta:
        model = Doctor
        fields = ["id", "full_name", "license_number", "specialization", "phone", "role"]

    def get_full_name(self, obj):
        user = obj.clinic_user.user
        return user.get_full_name() or user.username


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"


class ToothSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tooth
        fields = "__all__"


class ToothConditionSerializer(serializers.ModelSerializer):
    tooth_code = serializers.CharField(source="tooth.code", read_only=True)

    class Meta:
        model = ToothCondition
        fields = ["id", "patient", "tooth", "tooth_code", "condition", "note", "updated_at"]


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)

    class Meta:
        model = Appointment
        fields = "__all__"

    def validate(self, data):
        if data.get("end_at") <= data.get("start_at"):
            raise serializers.ValidationError("end_at must be after start_at")
        return data


class InvoiceSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        fields = ["id", "patient", "patient_name", "invoice_number", "total_amount", "paid_amount", "balance", "status", "issued_at"]
