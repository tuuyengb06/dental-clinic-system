from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from clinic.models import Doctor, Patient, Service, WorkSchedule
from .models import Appointment, MedicalRecord


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    patient_code = serializers.SerializerMethodField()
    dentist_name = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()
    can_open_medical_record = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = "__all__"

    def get_patient_name(self, appointment):
        try:
            patient = appointment.patient
        except ObjectDoesNotExist:
            return None
        return patient.full_name if patient is not None else None

    def get_patient_code(self, appointment):
        try:
            patient = appointment.patient
        except ObjectDoesNotExist:
            return None
        return patient.patient_code if patient is not None else None

    def get_dentist_name(self, appointment):
        try:
            doctor = appointment.doctor
            if doctor is None:
                return None
            clinic_user = doctor.clinic_user
            if clinic_user is None:
                return None
            user = clinic_user.user
        except ObjectDoesNotExist:
            return None
        if not user:
            return None
        return user.get_full_name().strip() or user.username

    def get_service_name(self, appointment):
        try:
            service = appointment.service
        except ObjectDoesNotExist:
            return None
        return service.name if service else None

    def get_can_open_medical_record(self, appointment):
        request = self.context.get('request')
        if request is None or not request.user.is_authenticated:
            return False

        if not hasattr(request, '_medical_record_doctor_id'):
            try:
                clinic_user = request.user.clinic_profile
                doctor = clinic_user.doctor_profile if clinic_user.role.code == 'DENTIST' else None
                request._medical_record_doctor_id = doctor.pk if doctor else None
            except ObjectDoesNotExist:
                request._medical_record_doctor_id = None

        return request._medical_record_doctor_id == appointment.doctor_id


class AppointmentBookingSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())

    class Meta:
        model = Appointment
        fields = ('patient', 'doctor', 'service', 'appointment_date', 'notes')
        extra_kwargs = {'notes': {'required': False, 'allow_blank': True}}

    def validate_service(self, service):
        if not service.is_active:
            raise serializers.ValidationError('Selected service is inactive.')
        if service.duration_minutes <= 0:
            raise serializers.ValidationError('Service duration must be greater than zero.')
        return service

    def create(self, validated_data):
        doctor_id = validated_data['doctor'].pk
        patient_id = validated_data['patient'].pk
        service_id = validated_data['service'].pk
        appointment_date = validated_data['appointment_date']
        local_start = timezone.localtime(appointment_date)

        with transaction.atomic():
            try:
                doctor = Doctor.objects.select_for_update().get(pk=doctor_id)
            except Doctor.DoesNotExist as error:
                raise serializers.ValidationError({
                    'doctor': 'Selected dentist does not exist.'
                }) from error
            try:
                patient = Patient.objects.select_for_update().get(pk=patient_id)
            except Patient.DoesNotExist as error:
                raise serializers.ValidationError({
                    'patient': 'Selected patient does not exist.'
                }) from error
            try:
                service = Service.objects.select_for_update().get(pk=service_id)
            except Service.DoesNotExist as error:
                raise serializers.ValidationError({
                    'service': 'Selected service does not exist.'
                }) from error
            if not service.is_active:
                raise serializers.ValidationError({'service': 'Selected service is inactive.'})

            local_end = local_start + timedelta(minutes=service.duration_minutes)
            if local_end.date() != local_start.date():
                raise serializers.ValidationError({
                    'appointment_date': 'Appointment must fit within one workday.'
                })

            works_during_appointment = WorkSchedule.objects.filter(
                doctor=doctor,
                work_date=local_start.date(),
                start_time__lte=local_start.time(),
                end_time__gte=local_end.time(),
            ).exists()
            if not works_during_appointment:
                raise serializers.ValidationError({
                    'appointment_date': 'The dentist is not working for the full appointment period.'
                })

            blocking_statuses = [Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
            existing_appointments = Appointment.objects.filter(
                doctor=doctor,
                status__in=blocking_statuses,
            ).select_related('service')
            for existing in existing_appointments:
                existing_start = timezone.localtime(existing.appointment_date)
                if not existing.service_id:
                    if existing_start.date() == local_start.date():
                        raise serializers.ValidationError({
                            'appointment_date': (
                                'An existing appointment for this dentist has no service duration; '
                                'another booking cannot be safely scheduled on that date.'
                            )
                        })
                    continue
                existing_duration = existing.service.duration_minutes
                existing_end = existing_start + timedelta(minutes=existing_duration)
                if local_start < existing_end and local_end > existing_start:
                    raise serializers.ValidationError({
                        'appointment_date': 'This time overlaps another appointment for the selected dentist.'
                    })

            validated_data['doctor'] = doctor
            validated_data['patient'] = patient
            validated_data['service'] = service
            return super().create(validated_data)


class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = "__all__"


class MedicalRecordReadSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='appointment.patient.full_name', read_only=True)
    patient_code = serializers.CharField(source='appointment.patient.patient_code', read_only=True)

    class Meta:
        model = MedicalRecord
        fields = (
            'id',
            'appointment',
            'patient_name',
            'patient_code',
            'diagnosis',
            'treatment_plan',
            'prescription',
            'notes',
            'created_at',
        )
        read_only_fields = fields


class MedicalRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = ('diagnosis', 'treatment_plan', 'prescription', 'notes')
        extra_kwargs = {
            'diagnosis': {'required': True, 'allow_blank': False},
            'treatment_plan': {'required': True, 'allow_blank': False},
            'prescription': {'required': False, 'allow_blank': True, 'allow_null': True},
            'notes': {'required': False, 'allow_blank': True, 'allow_null': True},
        }


class MedicalRecordUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = ('diagnosis', 'treatment_plan', 'prescription', 'notes')
        extra_kwargs = {
            'diagnosis': {'required': True, 'allow_blank': False},
            'treatment_plan': {'required': True, 'allow_blank': False},
            'prescription': {'required': False, 'allow_blank': True, 'allow_null': True},
            'notes': {'required': False, 'allow_blank': True, 'allow_null': True},
        }
