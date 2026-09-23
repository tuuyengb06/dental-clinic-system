from rest_framework import serializers
from .models import Appointment, Invoice, Patient, Tooth, ToothCondition


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
