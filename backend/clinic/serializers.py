from rest_framework import serializers
from .models import Appointment, Doctor, Patient, WorkSchedule, Service, Invoice

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


class ClinicAppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    type = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            "id", "patient", "patient_name", "dentist_name", "start_at",
            "end_at", "room", "status", "notes", "type",
        ]

    def get_type(self, appointment):
        return appointment.notes or "Dental consultation"


class InvoiceSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id", "patient", "invoice_number", "total_amount", "paid_amount",
            "balance", "status", "issued_at",
        ]
        read_only_fields = ["id", "issued_at"]