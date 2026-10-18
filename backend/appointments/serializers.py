from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers
from clinic.models import Tooth, WorkSchedule
from .models import Appointment, MedicalRecord


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    dentist_name = serializers.SerializerMethodField()
    service_name = serializers.CharField(source="service.name", read_only=True)
    start_at = serializers.DateTimeField(source="appointment_date", read_only=True)
    end_at = serializers.SerializerMethodField()
    type = serializers.CharField(source="service.name", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id", "patient", "patient_name", "doctor", "dentist_name",
            "service", "service_name", "appointment_date", "start_at",
            "end_at", "status", "notes", "type", "created_at",
        ]
        read_only_fields = ["id", "created_at", "status"]

    def get_dentist_name(self, appointment):
        user = appointment.doctor.clinic_user.user
        return user.get_full_name() or user.username

    def get_end_at(self, appointment):
        duration = appointment.service.duration_minutes if appointment.service_id else 30
        return appointment.appointment_date + timedelta(minutes=duration)

    def validate(self, attrs):
        instance = self.instance
        doctor = attrs.get("doctor", instance.doctor if instance else None)
        patient = attrs.get("patient", instance.patient if instance else None)
        service = attrs.get("service", instance.service if instance else None)
        appointment_date = attrs.get(
            "appointment_date", instance.appointment_date if instance else None
        )
        if not doctor or not service or not appointment_date:
            raise serializers.ValidationError(
                "Patient, dentist, service and appointment time are required."
            )
        if not service.is_active:
            raise serializers.ValidationError({"service": "This service is inactive."})

        local_start = timezone.localtime(appointment_date)
        local_end = local_start + timedelta(minutes=service.duration_minutes)
        shift_exists = WorkSchedule.objects.filter(
            doctor=doctor, work_date=local_start.date()
        ).exists()
        if not shift_exists or not WorkSchedule.objects.filter(
            doctor=doctor,
            work_date=local_start.date(),
            start_time__lte=local_start.time(),
            end_time__gte=local_end.time(),
        ).exists():
            raise serializers.ValidationError(
                {"appointment_date": "The dentist is not scheduled for this time."}
            )

        if not self._doctor_can_manage(doctor):
            raise serializers.ValidationError(
                {"doctor": "Dentists can only manage their own appointments."}
            )

        for existing in Appointment.objects.filter(
            Q(doctor=doctor) | Q(patient=patient),
            appointment_date__date=local_start.date(),
        ).exclude(pk=instance.pk if instance else None).exclude(
            status=Appointment.Status.CANCELLED
        ):
            existing_duration = existing.service.duration_minutes if existing.service_id else 30
            existing_start = timezone.localtime(existing.appointment_date)
            existing_end = existing_start + timedelta(minutes=existing_duration)
            if local_start < existing_end and existing_start < local_end:
                raise serializers.ValidationError(
                    {"appointment_date": "This time overlaps another appointment."}
                )
        return attrs

    def _doctor_can_manage(self, doctor):
        request = self.context.get("request")
        if request is None:
            return False
        user = request.user
        if user.is_superuser:
            return True
        clinic_profile = getattr(user, "clinic_profile", None)
        if not clinic_profile:
            return False
        if clinic_profile.role.code == "ADMIN":
            return True
        if clinic_profile.role.code == "DENTIST":
            return doctor.clinic_user_id == clinic_profile.id
        return clinic_profile.role.code == "RECEPTIONIST"


class MedicalRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="appointment.patient.full_name", read_only=True)
    appointment_date = serializers.DateTimeField(
        source="appointment.appointment_date", read_only=True
    )
    tooth_codes = serializers.SlugRelatedField(
        source="teeth",
        slug_field="code",
        many=True,
        read_only=True,
    )

    class Meta:
        model = MedicalRecord
        fields = [
            "id", "appointment", "patient_name", "appointment_date", "diagnosis",
            "treatment_plan", "prescription", "notes", "teeth", "tooth_codes",
            "services", "created_at",
            "follow_up_date",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        appointment = attrs.get(
            "appointment", self.instance.appointment if self.instance else None
        )
        teeth = attrs.get("teeth", self.instance.teeth.all() if self.instance else [])
        if appointment:
            if appointment.status == Appointment.Status.CANCELLED:
                raise serializers.ValidationError(
                    {"appointment": "Cancelled appointments cannot receive a medical record."}
                )
            follow_up_date = attrs.get(
                "follow_up_date",
                self.instance.follow_up_date if self.instance else None,
            )
            if follow_up_date and follow_up_date < timezone.localdate(
                appointment.appointment_date
            ):
                raise serializers.ValidationError(
                    {"follow_up_date": "Follow-up date cannot be before the appointment."}
                )
            if any(tooth.dentition_type != appointment.patient.dentition_type for tooth in teeth):
                raise serializers.ValidationError(
                    {"teeth": "Selected teeth must match the patient's dentition type."}
                )
        return attrs

    def validate_appointment(self, appointment):
        request = self.context.get("request")
        if request is None:
            raise serializers.ValidationError("Authenticated user context is required.")
        clinic_profile = getattr(request.user, "clinic_profile", None)
        if (
            not request.user.is_superuser
            and (
                not clinic_profile
                or (
                    clinic_profile.role.code == "DENTIST"
                    and appointment.doctor_id != getattr(
                        getattr(clinic_profile, "doctor_profile", None), "id", None
                    )
                )
            )
        ):
            raise serializers.ValidationError(
                "You can only document appointments assigned to you."
            )
        return appointment

    def validate_services(self, services):
        if any(not service.is_active for service in services):
            raise serializers.ValidationError("Inactive services cannot be prescribed.")
        return services