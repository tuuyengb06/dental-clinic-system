from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Appointment, MedicalRecord
from .serializers import (
    AppointmentBookingSerializer,
    AppointmentSerializer,
    MedicalRecordCreateSerializer,
    MedicalRecordReadSerializer,
    MedicalRecordSerializer,
    MedicalRecordUpdateSerializer,
)


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def _current_clinic_doctor(self):
        try:
            clinic_user = self.request.user.clinic_profile
            if clinic_user.role.code != 'DENTIST':
                return None
            return clinic_user.doctor_profile
        except ObjectDoesNotExist:
            return None

    def get_queryset(self):
        queryset = Appointment.objects.all()
        if not self.request.path.startswith('/api/v1/'):
            return queryset
        try:
            clinic_user = self.request.user.clinic_profile
        except ObjectDoesNotExist:
            return queryset

        if clinic_user.role.code != 'DENTIST':
            return queryset
        doctor = self._current_clinic_doctor()
        if doctor is None:
            raise PermissionDenied('This dentist account is not linked to a doctor record.')
        return queryset.filter(doctor=doctor)

    def create_booking(self, request, *args, **kwargs):
        booking_serializer = AppointmentBookingSerializer(data=request.data)
        booking_serializer.is_valid(raise_exception=True)
        appointment = booking_serializer.save()
        return Response(
            AppointmentSerializer(appointment, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    def cancel_booking(self, request, *args, **kwargs):
        with transaction.atomic():
            try:
                appointment = Appointment.objects.select_for_update().get(pk=kwargs['pk'])
            except Appointment.DoesNotExist as error:
                raise NotFound('Appointment not found.') from error

            if appointment.status == Appointment.Status.CANCELLED:
                return Response(
                    {'detail': 'This appointment has already been cancelled.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if appointment.status == Appointment.Status.COMPLETED:
                return Response(
                    {'detail': 'A completed appointment cannot be cancelled.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if appointment.status not in (Appointment.Status.PENDING, Appointment.Status.CONFIRMED):
                return Response(
                    {'detail': 'This appointment cannot be cancelled in its current status.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            appointment.status = Appointment.Status.CANCELLED
            appointment.save(update_fields=['status'])

        return Response(
            AppointmentSerializer(appointment, context=self.get_serializer_context()).data,
            status=status.HTTP_200_OK,
        )

    def medical_record(self, request, *args, **kwargs):
        doctor = self._current_clinic_doctor()
        if doctor is None:
            raise PermissionDenied('Only the dentist assigned to this appointment can view its medical record.')

        try:
            appointment = Appointment.objects.select_related('patient', 'doctor').get(pk=kwargs['pk'])
        except Appointment.DoesNotExist as error:
            raise NotFound('Appointment not found.') from error

        if appointment.patient_id is None or appointment.doctor_id is None:
            raise NotFound('Appointment is missing its patient or assigned dentist.')
        if appointment.doctor_id != doctor.pk:
            raise PermissionDenied('You can only view records for appointments assigned to you.')

        try:
            record = MedicalRecord.objects.select_related('appointment__patient').get(appointment=appointment)
        except MedicalRecord.DoesNotExist:
            return Response(
                {
                    'detail': 'This appointment does not have a medical record yet.',
                    'code': 'medical_record_not_found',
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            MedicalRecordReadSerializer(record, context=self.get_serializer_context()).data,
            status=status.HTTP_200_OK,
        )

    def create_medical_record(self, request, *args, **kwargs):
        doctor = self._current_clinic_doctor()
        if doctor is None:
            raise PermissionDenied('Only the dentist assigned to this appointment can create its medical record.')

        try:
            with transaction.atomic():
                try:
                    appointment = Appointment.objects.select_for_update().get(pk=kwargs['pk'])
                except Appointment.DoesNotExist as error:
                    raise NotFound('Appointment not found.') from error

                if appointment.patient_id is None or appointment.doctor_id is None:
                    raise NotFound('Appointment is missing its patient or assigned dentist.')
                if appointment.doctor_id != doctor.pk:
                    raise PermissionDenied('You can only create records for appointments assigned to you.')

                if MedicalRecord.objects.filter(appointment=appointment).exists():
                    return Response(
                        {
                            'detail': 'A medical record already exists for this appointment. Open the existing record.',
                            'code': 'medical_record_exists',
                        },
                        status=status.HTTP_409_CONFLICT,
                    )

                eligible_statuses = (Appointment.Status.CONFIRMED, Appointment.Status.COMPLETED)
                if appointment.status not in eligible_statuses:
                    return Response(
                        {
                            'detail': 'A medical record can only be created for a confirmed or completed appointment.',
                            'code': 'appointment_status_not_eligible',
                        },
                        status=status.HTTP_409_CONFLICT,
                    )

                serializer = MedicalRecordCreateSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                record = serializer.save(appointment=appointment)
        except IntegrityError:
            if MedicalRecord.objects.filter(appointment_id=kwargs['pk']).exists():
                return Response(
                    {
                        'detail': 'A medical record already exists for this appointment. Open the existing record.',
                        'code': 'medical_record_exists',
                    },
                    status=status.HTTP_409_CONFLICT,
                )
            raise

        return Response(
            MedicalRecordReadSerializer(record, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    def update_medical_record(self, request, *args, **kwargs):
        doctor = self._current_clinic_doctor()
        if doctor is None:
            raise PermissionDenied('Only the dentist assigned to this appointment can update its medical record.')

        with transaction.atomic():
            try:
                record = MedicalRecord.objects.select_for_update().select_related('appointment').get(
                    appointment_id=kwargs['pk'],
                )
            except MedicalRecord.DoesNotExist as error:
                raise NotFound('Medical record not found for this appointment.') from error

            if record.appointment.doctor_id != doctor.pk:
                raise PermissionDenied('You can only update records for appointments assigned to you.')

            serializer = MedicalRecordUpdateSerializer(
                record,
                data=request.data,
                partial=request.method == 'PATCH',
            )
            serializer.is_valid(raise_exception=True)
            record = serializer.save()

        record = MedicalRecord.objects.select_related('appointment__patient').get(pk=record.pk)
        return Response(
            MedicalRecordReadSerializer(record, context=self.get_serializer_context()).data,
            status=status.HTTP_200_OK,
        )


class MedicalRecordViewSet(viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated]
