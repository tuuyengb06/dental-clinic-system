from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from clinic.models import ClinicUser, Doctor, Patient, Role, Service
from .models import Appointment


User = get_user_model()


class AppointmentCancellationApiTests(TestCase):
    def setUp(self):
        receptionist_role = Role.objects.create(code="RECEPTIONIST", name="Receptionist")
        dentist_role = Role.objects.create(code="DENTIST", name="Dentist")
        receptionist = User.objects.create_user(username="front-desk", password="test-pass")
        self.dentist_user = User.objects.create_user(username="dentist", password="test-pass")
        ClinicUser.objects.create(user=receptionist, role=receptionist_role)
        dentist_profile = ClinicUser.objects.create(user=self.dentist_user, role=dentist_role)
        self.doctor = Doctor.objects.create(
            clinic_user=dentist_profile,
            license_number="CANCEL-TEST-001",
            specialization="General dentistry",
        )
        self.patient = Patient.objects.create(
            patient_code="CANCEL-TEST-001",
            full_name="Cancellation Test Patient",
        )
        self.service = Service.objects.create(
            code="CANCEL-TEST",
            name="Cancellation test",
            price="100000",
        )
        self.client = APIClient()
        self.client.force_authenticate(receptionist)

    def create_appointment(self, appointment_status):
        return Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            service=self.service,
            appointment_date=timezone.now() + timedelta(days=1),
            status=appointment_status,
        )

    def cancel(self, appointment):
        return self.client.post(f"/api/v1/appointments/{appointment.id}/cancel/")

    def test_pending_appointment_can_be_cancelled(self):
        appointment = self.create_appointment(Appointment.Status.PENDING)

        response = self.cancel(appointment)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Appointment.Status.CANCELLED)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.CANCELLED)

    def test_confirmed_appointment_can_be_cancelled(self):
        appointment = self.create_appointment(Appointment.Status.CONFIRMED)

        response = self.cancel(appointment)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Appointment.Status.CANCELLED)

    def test_already_cancelled_appointment_returns_clear_validation_error(self):
        appointment = self.create_appointment(Appointment.Status.CANCELLED)

        response = self.cancel(appointment)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data["status"]), "This appointment is already cancelled.")

    def test_completed_appointment_cannot_be_cancelled(self):
        appointment = self.create_appointment(Appointment.Status.COMPLETED)

        response = self.cancel(appointment)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data["status"]),
            "Only pending or confirmed appointments can be cancelled.",
        )
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.COMPLETED)

    def test_dentist_cannot_cancel_an_appointment(self):
        appointment = self.create_appointment(Appointment.Status.PENDING)
        self.client.force_authenticate(self.dentist_user)

        response = self.cancel(appointment)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.PENDING)
