from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, time, timedelta
from threading import Barrier

from django.contrib.auth import get_user_model
from django.db import close_old_connections
from django.test import TransactionTestCase
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

from clinic.models import ClinicUser, Doctor, Patient, Role, Service, WorkSchedule
from .models import Appointment, MedicalRecord


class AppointmentBookingDataMixin:
    def setUp(self):
        super().setUp()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='appointment-test-user',
            password='TestPass123!',
        )
        dentist_user = user_model.objects.create_user(
            username='appointment-test-dentist',
            first_name='Test',
            last_name='Dentist',
            role='Doctor',
        )
        self.dentist_user = dentist_user
        dentist_role = Role.objects.create(code='DENTIST', name='Dentist')
        clinic_user = ClinicUser.objects.create(user=dentist_user, role=dentist_role)
        self.doctor = Doctor.objects.create(
            clinic_user=clinic_user,
            license_number='TEST-APPT-001',
        )
        self.patient = Patient.objects.create(
            patient_code='TEST-APPT-001',
            full_name='Appointment Test Patient',
        )
        self.service = Service.objects.create(
            code='TEST-APPT-CHECK',
            name='Test check-up',
            price='100000',
            duration_minutes=30,
        )
        self.work_date = timezone.localdate() + timedelta(days=2)
        WorkSchedule.objects.create(
            doctor=self.doctor,
            work_date=self.work_date,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        self.appointment_datetime = timezone.make_aware(
            datetime.combine(self.work_date, time(10, 0))
        )
        if hasattr(self.client, 'force_authenticate'):
            self.client.force_authenticate(user=self.user)

    def booking_payload(self, **overrides):
        payload = {
            'patient': self.patient.pk,
            'doctor': self.doctor.pk,
            'service': self.service.pk,
            'appointment_date': self.appointment_datetime.isoformat(),
            'notes': 'Routine examination',
        }
        payload.update(overrides)
        return payload


class AppointmentBookingApiTests(AppointmentBookingDataMixin, APITestCase):
    endpoint = '/api/v1/appointments/'

    def test_valid_booking_is_created_and_visible_through_slice_one_reads(self):
        created = self.client.post(self.endpoint, self.booking_payload(), format='json')

        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data['status'], Appointment.Status.PENDING)
        self.assertEqual(created.data['patient_name'], self.patient.full_name)
        self.assertEqual(created.data['dentist_name'], 'Test Dentist')
        self.assertEqual(created.data['service_name'], self.service.name)

        listing = self.client.get(self.endpoint)
        detail = self.client.get(f'{self.endpoint}{created.data["id"]}/')
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(len(listing.data), 1)
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data['id'], created.data['id'])

    def test_missing_required_fields_are_rejected(self):
        response = self.client.post(self.endpoint, {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('patient', response.data)
        self.assertIn('doctor', response.data)
        self.assertIn('service', response.data)
        self.assertIn('appointment_date', response.data)

    def test_unknown_patient_and_doctor_are_rejected(self):
        unknown_patient = self.client.post(
            self.endpoint,
            self.booking_payload(patient=999999),
            format='json',
        )
        unknown_doctor = self.client.post(
            self.endpoint,
            self.booking_payload(doctor=999999),
            format='json',
        )
        self.assertEqual(unknown_patient.status_code, 400)
        self.assertEqual(unknown_doctor.status_code, 400)

    def test_invalid_date_and_inactive_service_are_rejected(self):
        invalid_date = self.client.post(
            self.endpoint,
            self.booking_payload(appointment_date='not-a-date'),
            format='json',
        )
        self.service.is_active = False
        self.service.save(update_fields=['is_active'])
        inactive_service = self.client.post(
            self.endpoint,
            self.booking_payload(),
            format='json',
        )
        self.assertEqual(invalid_date.status_code, 400)
        self.assertEqual(inactive_service.status_code, 400)

    def test_dentist_must_work_for_the_entire_service_duration(self):
        outside_shift = timezone.make_aware(
            datetime.combine(self.work_date, time(16, 45))
        )
        response = self.client.post(
            self.endpoint,
            self.booking_payload(appointment_date=outside_shift.isoformat()),
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('appointment_date', response.data)

    def test_overlapping_pending_or_confirmed_appointments_are_rejected(self):
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            service=self.service,
            appointment_date=self.appointment_datetime,
            status=Appointment.Status.CONFIRMED,
        )
        overlapping_start = timezone.make_aware(
            datetime.combine(self.work_date, time(10, 15))
        )
        response = self.client.post(
            self.endpoint,
            self.booking_payload(appointment_date=overlapping_start.isoformat()),
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('overlaps', str(response.data).lower())

    def test_cancelled_and_completed_appointments_do_not_block_booking(self):
        for status in (Appointment.Status.CANCELLED, Appointment.Status.COMPLETED):
            Appointment.objects.create(
                patient=self.patient,
                doctor=self.doctor,
                service=self.service,
                appointment_date=self.appointment_datetime,
                status=status,
            )
        response = self.client.post(self.endpoint, self.booking_payload(), format='json')
        self.assertEqual(response.status_code, 201)

    def test_existing_booking_without_service_blocks_same_day_safely(self):
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            service=None,
            appointment_date=self.appointment_datetime,
            status=Appointment.Status.PENDING,
        )
        response = self.client.post(self.endpoint, self.booking_payload(), format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('no service duration', str(response.data).lower())

    def test_legacy_appointment_get_endpoint_remains_available(self):
        response = self.client.get('/api/appointments/')
        self.assertEqual(response.status_code, 200)


class AppointmentCancellationApiTests(AppointmentBookingDataMixin, APITestCase):
    endpoint = '/api/v1/appointments/'

    def make_appointment(self, status):
        return Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            service=self.service,
            appointment_date=self.appointment_datetime,
            status=status,
            notes='Preserve this appointment history',
        )

    def test_pending_and_confirmed_appointments_are_cancelled_without_losing_history(self):
        for original_status in (Appointment.Status.PENDING, Appointment.Status.CONFIRMED):
            with self.subTest(status=original_status):
                appointment = self.make_appointment(original_status)
                response = self.client.post(f'{self.endpoint}{appointment.pk}/cancel/')

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data['status'], Appointment.Status.CANCELLED)
                appointment.refresh_from_db()
                self.assertEqual(appointment.status, Appointment.Status.CANCELLED)
                self.assertEqual(appointment.patient_id, self.patient.pk)
                self.assertEqual(appointment.doctor_id, self.doctor.pk)
                self.assertEqual(appointment.service_id, self.service.pk)
                self.assertEqual(appointment.appointment_date, self.appointment_datetime)
                self.assertEqual(appointment.notes, 'Preserve this appointment history')
                self.assertTrue(Appointment.objects.filter(pk=appointment.pk).exists())

    def test_missing_appointment_returns_404(self):
        response = self.client.post(f'{self.endpoint}999999/cancel/')
        self.assertEqual(response.status_code, 404)
        self.assertIn('not found', response.data['detail'].lower())

    def test_already_cancelled_appointment_is_rejected(self):
        appointment = self.make_appointment(Appointment.Status.CANCELLED)
        response = self.client.post(f'{self.endpoint}{appointment.pk}/cancel/')
        self.assertEqual(response.status_code, 400)
        self.assertIn('already been cancelled', response.data['detail'].lower())

    def test_completed_appointment_cannot_be_cancelled(self):
        appointment = self.make_appointment(Appointment.Status.COMPLETED)
        response = self.client.post(f'{self.endpoint}{appointment.pk}/cancel/')
        self.assertEqual(response.status_code, 400)
        self.assertIn('completed appointment', response.data['detail'].lower())
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.COMPLETED)

    def test_get_list_and_detail_return_cancelled_status_and_cancelled_slot_is_reusable(self):
        appointment = self.make_appointment(Appointment.Status.PENDING)
        cancelled = self.client.post(f'{self.endpoint}{appointment.pk}/cancel/')
        listing = self.client.get(self.endpoint)
        detail = self.client.get(f'{self.endpoint}{appointment.pk}/')
        self.assertEqual(cancelled.status_code, 200)
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.data[0]['status'], Appointment.Status.CANCELLED)
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data['status'], Appointment.Status.CANCELLED)

        new_booking = self.client.post(self.endpoint, self.booking_payload(), format='json')
        self.assertEqual(new_booking.status_code, 201)


class AppointmentCancellationConcurrencyTests(AppointmentBookingDataMixin, TransactionTestCase):
    reset_sequences = True

    def test_simultaneous_cancellations_only_report_one_first_cancellation(self):
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            service=self.service,
            appointment_date=self.appointment_datetime,
            status=Appointment.Status.PENDING,
        )
        barrier = Barrier(2)
        user_id = self.user.pk

        def cancel_appointment():
            close_old_connections()
            try:
                client = APIClient()
                client.force_authenticate(user=get_user_model().objects.get(pk=user_id))
                barrier.wait(timeout=10)
                return client.post(f'/api/v1/appointments/{appointment.pk}/cancel/').status_code
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            statuses = list(executor.map(lambda _: cancel_appointment(), range(2)))

        self.assertCountEqual(statuses, [200, 400])
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.CANCELLED)


class MedicalRecordReadApiTests(AppointmentBookingDataMixin, APITestCase):
    endpoint = '/api/v1/appointments/'

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.dentist_user)
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            service=self.service,
            appointment_date=self.appointment_datetime,
            status=Appointment.Status.CONFIRMED,
            notes='Appointment notes remain private to the appointment response.',
        )

    def create_medical_record(self, appointment=None):
        return MedicalRecord.objects.create(
            appointment=appointment or self.appointment,
            diagnosis='Existing diagnosis',
            treatment_plan='Existing treatment plan',
            prescription='Existing prescription',
            notes='Existing clinical notes',
        )

    def test_assigned_dentist_can_read_existing_record_without_mutating_data(self):
        record = self.create_medical_record()
        appointment_updated_at = self.appointment.appointment_date
        response = self.client.get(f'{self.endpoint}{self.appointment.pk}/medical-record/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['patient_name'], self.patient.full_name)
        self.assertEqual(response.data['patient_code'], self.patient.patient_code)
        self.assertEqual(response.data['diagnosis'], record.diagnosis)
        self.assertEqual(response.data['treatment_plan'], record.treatment_plan)
        self.assertEqual(response.data['prescription'], record.prescription)
        self.assertEqual(response.data['notes'], record.notes)
        self.assertNotIn('medical_history', response.data)
        self.assertNotIn('phone', response.data)

        record.refresh_from_db()
        self.appointment.refresh_from_db()
        self.assertEqual(record.diagnosis, 'Existing diagnosis')
        self.assertEqual(self.appointment.appointment_date, appointment_updated_at)
        self.assertEqual(MedicalRecord.objects.count(), 1)

    def test_appointment_response_marks_only_the_assigned_dentist_as_record_reader(self):
        response = self.client.get(f'{self.endpoint}{self.appointment.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['can_open_medical_record'])

        self.client.force_authenticate(user=self.user)
        non_dentist_response = self.client.get(f'{self.endpoint}{self.appointment.pk}/')
        self.assertEqual(non_dentist_response.status_code, 200)
        self.assertFalse(non_dentist_response.data['can_open_medical_record'])

    def test_appointment_without_record_returns_specific_404_and_creates_nothing(self):
        response = self.client.get(f'{self.endpoint}{self.appointment.pk}/medical-record/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['code'], 'medical_record_not_found')
        self.assertEqual(MedicalRecord.objects.count(), 0)

    def test_unknown_appointment_returns_404(self):
        response = self.client.get(f'{self.endpoint}999999/medical-record/')
        self.assertEqual(response.status_code, 404)
        self.assertNotEqual(response.data.get('code'), 'medical_record_not_found')

    def test_unauthenticated_user_cannot_read_record(self):
        self.create_medical_record()
        self.client.force_authenticate(user=None)
        response = self.client.get(f'{self.endpoint}{self.appointment.pk}/medical-record/')
        self.assertEqual(response.status_code, 401)

    def test_non_dentist_cannot_read_record(self):
        self.create_medical_record()
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'{self.endpoint}{self.appointment.pk}/medical-record/')
        self.assertEqual(response.status_code, 403)

    def test_dentist_cannot_access_another_dentists_appointment_or_record_by_id(self):
        other_user = get_user_model().objects.create_user(username='other-dentist', role='Doctor')
        other_clinic_user = ClinicUser.objects.create(user=other_user, role=self.doctor.clinic_user.role)
        other_doctor = Doctor.objects.create(
            clinic_user=other_clinic_user,
            license_number='OTHER-APPT-DOC',
        )
        other_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=other_doctor,
            service=self.service,
            appointment_date=self.appointment_datetime + timedelta(hours=1),
            status=Appointment.Status.CONFIRMED,
        )
        other_record = self.create_medical_record(other_appointment)

        appointment_list = self.client.get(self.endpoint)
        appointment_detail = self.client.get(f'{self.endpoint}{other_appointment.pk}/')
        medical_record = self.client.get(f'{self.endpoint}{other_appointment.pk}/medical-record/')
        self.assertEqual(appointment_list.status_code, 200)
        self.assertEqual([row['id'] for row in appointment_list.data], [self.appointment.pk])
        self.assertEqual(appointment_detail.status_code, 404)
        self.assertEqual(medical_record.status_code, 403)
        self.assertTrue(MedicalRecord.objects.filter(pk=other_record.pk).exists())

        legacy_list = self.client.get('/api/appointments/')
        self.assertEqual(legacy_list.status_code, 200)
        self.assertEqual(len(legacy_list.data), 2)

    def test_post_does_not_overwrite_an_existing_medical_record(self):
        record = self.create_medical_record()
        response = self.client.post(
            f'{self.endpoint}{self.appointment.pk}/medical-record/',
            {'diagnosis': 'Attempted modification'},
            format='json',
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data['code'], 'medical_record_exists')
        record.refresh_from_db()
        self.assertEqual(record.diagnosis, 'Existing diagnosis')


class MedicalRecordCreateApiTests(AppointmentBookingDataMixin, APITestCase):
    endpoint = '/api/v1/appointments/'

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.dentist_user)
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            service=self.service,
            appointment_date=self.appointment_datetime,
            status=Appointment.Status.CONFIRMED,
            notes='Original appointment notes',
        )
        self.payload = {
            'diagnosis': 'Dental caries',
            'treatment_plan': 'Restore tooth 16',
            'prescription': 'Pain relief as needed',
            'notes': 'Patient advised to return for review',
        }

    def test_assigned_dentist_creates_record_linked_to_verified_appointment_and_can_read_it(self):
        response = self.client.post(
            f'{self.endpoint}{self.appointment.pk}/medical-record/',
            self.payload,
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        record = MedicalRecord.objects.get(appointment=self.appointment)
        self.assertEqual(record.appointment_id, self.appointment.pk)
        self.assertEqual(record.appointment.patient_id, self.patient.pk)
        self.assertEqual(record.appointment.doctor_id, self.doctor.pk)
        self.assertEqual(response.data['patient_name'], self.patient.full_name)
        self.assertEqual(response.data['diagnosis'], self.payload['diagnosis'])
        self.assertEqual(self.appointment.notes, 'Original appointment notes')
        self.assertEqual(MedicalRecord.objects.count(), 1)

        opened = self.client.get(f'{self.endpoint}{self.appointment.pk}/medical-record/')
        self.assertEqual(opened.status_code, 200)
        self.assertEqual(opened.data['id'], response.data['id'])

    def test_required_fields_are_validated_without_partial_record(self):
        response = self.client.post(
            f'{self.endpoint}{self.appointment.pk}/medical-record/',
            {'diagnosis': 'Dental caries'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('treatment_plan', response.data)
        self.assertEqual(MedicalRecord.objects.count(), 0)

    def test_completed_appointment_can_receive_record_without_status_change(self):
        self.appointment.status = Appointment.Status.COMPLETED
        self.appointment.save(update_fields=['status'])
        response = self.client.post(
            f'{self.endpoint}{self.appointment.pk}/medical-record/',
            self.payload,
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, Appointment.Status.COMPLETED)

    def test_nonexistent_appointment_returns_404(self):
        response = self.client.post(
            f'{self.endpoint}999999/medical-record/',
            self.payload,
            format='json',
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(MedicalRecord.objects.count(), 0)

    def test_unauthenticated_and_non_dentist_users_are_denied(self):
        self.client.force_authenticate(user=None)
        unauthenticated = self.client.post(
            f'{self.endpoint}{self.appointment.pk}/medical-record/',
            self.payload,
            format='json',
        )
        self.assertEqual(unauthenticated.status_code, 401)

        self.client.force_authenticate(user=self.user)
        non_dentist = self.client.post(
            f'{self.endpoint}{self.appointment.pk}/medical-record/',
            self.payload,
            format='json',
        )
        self.assertEqual(non_dentist.status_code, 403)
        self.assertEqual(MedicalRecord.objects.count(), 0)

    def test_dentist_cannot_create_for_another_dentists_appointment(self):
        other_user = get_user_model().objects.create_user(username='other-record-doctor', role='Doctor')
        other_clinic_user = ClinicUser.objects.create(user=other_user, role=self.doctor.clinic_user.role)
        other_doctor = Doctor.objects.create(
            clinic_user=other_clinic_user,
            license_number='OTHER-RECORD-DOC',
        )
        other_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=other_doctor,
            service=self.service,
            appointment_date=self.appointment_datetime + timedelta(hours=1),
            status=Appointment.Status.CONFIRMED,
        )
        response = self.client.post(
            f'{self.endpoint}{other_appointment.pk}/medical-record/',
            self.payload,
            format='json',
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(MedicalRecord.objects.count(), 0)

    def test_pending_and_cancelled_appointments_cannot_receive_records(self):
        for appointment_status in (Appointment.Status.PENDING, Appointment.Status.CANCELLED):
            with self.subTest(status=appointment_status):
                self.appointment.status = appointment_status
                self.appointment.save(update_fields=['status'])
                response = self.client.post(
                    f'{self.endpoint}{self.appointment.pk}/medical-record/',
                    self.payload,
                    format='json',
                )
                self.assertEqual(response.status_code, 409)
                self.assertEqual(response.data['code'], 'appointment_status_not_eligible')
                self.assertFalse(MedicalRecord.objects.filter(appointment=self.appointment).exists())

    def test_duplicate_record_is_rejected_and_existing_record_is_preserved(self):
        existing = MedicalRecord.objects.create(
            appointment=self.appointment,
            diagnosis='Original diagnosis',
            treatment_plan='Original plan',
        )
        response = self.client.post(
            f'{self.endpoint}{self.appointment.pk}/medical-record/',
            self.payload,
            format='json',
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data['code'], 'medical_record_exists')
        self.assertEqual(MedicalRecord.objects.count(), 1)
        existing.refresh_from_db()
        self.assertEqual(existing.diagnosis, 'Original diagnosis')

    def test_patient_and_doctor_ids_from_client_are_not_accepted(self):
        response = self.client.post(
            f'{self.endpoint}{self.appointment.pk}/medical-record/',
            {**self.payload, 'patient': 999999, 'doctor': 999999},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        record = MedicalRecord.objects.get(appointment=self.appointment)
        self.assertEqual(record.appointment.patient_id, self.patient.pk)
        self.assertEqual(record.appointment.doctor_id, self.doctor.pk)


class MedicalRecordCreateConcurrencyTests(AppointmentBookingDataMixin, TransactionTestCase):
    reset_sequences = True

    def test_simultaneous_create_requests_for_one_appointment_only_create_one_record(self):
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            service=self.service,
            appointment_date=self.appointment_datetime,
            status=Appointment.Status.CONFIRMED,
        )
        barrier = Barrier(2)
        user_id = self.dentist_user.pk
        payload = {'diagnosis': 'Diagnosis', 'treatment_plan': 'Treatment'}

        def create_record():
            close_old_connections()
            try:
                client = APIClient()
                client.force_authenticate(user=get_user_model().objects.get(pk=user_id))
                barrier.wait(timeout=10)
                return client.post(
                    f'/api/v1/appointments/{appointment.pk}/medical-record/',
                    payload,
                    format='json',
                ).status_code
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            statuses = list(executor.map(lambda _: create_record(), range(2)))

        self.assertCountEqual(statuses, [201, 409])
        self.assertEqual(MedicalRecord.objects.filter(appointment=appointment).count(), 1)


class MedicalRecordUpdateApiTests(AppointmentBookingDataMixin, APITestCase):
    endpoint = '/api/v1/appointments/'

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.dentist_user)
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            service=self.service,
            appointment_date=self.appointment_datetime,
            status=Appointment.Status.COMPLETED,
        )
        self.record = MedicalRecord.objects.create(
            appointment=self.appointment,
            diagnosis='Original diagnosis',
            treatment_plan='Original treatment plan',
            prescription='Original prescription',
            notes='Original notes',
        )

    def test_assigned_dentist_can_partially_update_and_reopen_saved_record(self):
        response = self.client.patch(
            f'{self.endpoint}{self.appointment.pk}/medical-record/',
            {'diagnosis': 'Updated diagnosis'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['diagnosis'], 'Updated diagnosis')
        self.record.refresh_from_db()
        self.assertEqual(self.record.treatment_plan, 'Original treatment plan')
        self.assertEqual(self.record.prescription, 'Original prescription')
        self.assertEqual(self.record.notes, 'Original notes')
        self.assertEqual(self.record.appointment_id, self.appointment.pk)

        reopened = self.client.get(f'{self.endpoint}{self.appointment.pk}/medical-record/')
        self.assertEqual(reopened.status_code, 200)
        self.assertEqual(reopened.data['diagnosis'], 'Updated diagnosis')

    def test_invalid_full_update_is_rejected_without_overwriting_existing_values(self):
        response = self.client.put(
            f'{self.endpoint}{self.appointment.pk}/medical-record/',
            {'diagnosis': 'New diagnosis'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.record.refresh_from_db()
        self.assertEqual(self.record.diagnosis, 'Original diagnosis')
        self.assertEqual(self.record.treatment_plan, 'Original treatment plan')

    def test_missing_record_returns_404(self):
        other_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            service=self.service,
            appointment_date=self.appointment_datetime + timedelta(hours=1),
            status=Appointment.Status.COMPLETED,
        )
        response = self.client.patch(
            f'{self.endpoint}{other_appointment.pk}/medical-record/',
            {'diagnosis': 'New diagnosis'},
            format='json',
        )
        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_and_non_dentist_users_cannot_update(self):
        self.client.force_authenticate(user=None)
        unauthenticated = self.client.patch(
            f'{self.endpoint}{self.appointment.pk}/medical-record/',
            {'diagnosis': 'Changed'},
            format='json',
        )
        self.assertEqual(unauthenticated.status_code, 401)

        self.client.force_authenticate(user=self.user)
        non_dentist = self.client.patch(
            f'{self.endpoint}{self.appointment.pk}/medical-record/',
            {'diagnosis': 'Changed'},
            format='json',
        )
        self.assertEqual(non_dentist.status_code, 403)
        self.record.refresh_from_db()
        self.assertEqual(self.record.diagnosis, 'Original diagnosis')

    def test_dentist_cannot_update_record_from_another_dentists_appointment(self):
        other_user = get_user_model().objects.create_user(username='other-update-doctor', role='Doctor')
        other_clinic_user = ClinicUser.objects.create(user=other_user, role=self.doctor.clinic_user.role)
        other_doctor = Doctor.objects.create(
            clinic_user=other_clinic_user,
            license_number='OTHER-UPDATE-DOC',
        )
        other_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=other_doctor,
            service=self.service,
            appointment_date=self.appointment_datetime + timedelta(hours=1),
            status=Appointment.Status.COMPLETED,
        )
        other_record = MedicalRecord.objects.create(
            appointment=other_appointment,
            diagnosis='Other doctor diagnosis',
            treatment_plan='Other doctor plan',
        )
        response = self.client.patch(
            f'{self.endpoint}{other_appointment.pk}/medical-record/',
            {'diagnosis': 'Unauthorized change'},
            format='json',
        )
        self.assertEqual(response.status_code, 403)
        other_record.refresh_from_db()
        self.assertEqual(other_record.diagnosis, 'Other doctor diagnosis')

    def test_relationship_fields_are_not_mutable(self):
        response = self.client.patch(
            f'{self.endpoint}{self.appointment.pk}/medical-record/',
            {'diagnosis': 'Updated diagnosis', 'appointment': 999999},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.record.refresh_from_db()
        self.assertEqual(self.record.appointment_id, self.appointment.pk)


class AppointmentBookingConcurrencyTests(AppointmentBookingDataMixin, TransactionTestCase):
    reset_sequences = True

    def test_simultaneous_overlapping_bookings_for_one_dentist_do_not_both_succeed(self):
        barrier = Barrier(2)
        user_id = self.user.pk
        payload = self.booking_payload()

        def submit_booking():
            close_old_connections()
            try:
                client = APIClient()
                client.force_authenticate(user=get_user_model().objects.get(pk=user_id))
                barrier.wait(timeout=10)
                return client.post('/api/v1/appointments/', payload, format='json').status_code
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            statuses = list(executor.map(lambda _: submit_booking(), range(2)))

        self.assertCountEqual(statuses, [201, 400])
        self.assertEqual(
            Appointment.objects.filter(
                doctor=self.doctor,
                status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
            ).count(),
            1,
        )
