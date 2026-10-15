from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from clinic.models import ClinicUser, Doctor, Patient, Role, Service, Tooth
from .models import Appointment, MedicalRecord


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


class MedicalRecordApiTests(TestCase):
    def setUp(self):
        dentist_role = Role.objects.create(code="DENTIST", name="Dentist")
        self.dentist_user = User.objects.create_user(username="record-dentist", password="test-pass")
        dentist_profile = ClinicUser.objects.create(user=self.dentist_user, role=dentist_role)
        self.doctor = Doctor.objects.create(
            clinic_user=dentist_profile,
            license_number="RECORD-TEST-001",
            specialization="General dentistry",
        )
        self.patient = Patient.objects.create(
            patient_code="RECORD-TEST-001",
            full_name="Medical Record Test Patient",
        )
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            status=Appointment.Status.CONFIRMED,
        )
        self.tooth = Tooth.objects.create(
            code="A01",
            dentition_type=Patient.ADULT,
            display_order=1,
        )
        self.service = Service.objects.create(
            code="RECORD-TEST",
            name="Medical record test service",
            price="100000",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.dentist_user)

    def test_dentist_can_create_retrieve_and_update_medical_record(self):
        create_response = self.client.post(
            "/api/v1/medical-records/",
            {
                "appointment": self.appointment.id,
                "diagnosis": "Initial diagnosis",
                "treatment_plan": "Initial treatment plan",
                "teeth": [self.tooth.id],
                "services": [self.service.id],
                "notes": "Initial examination notes",
            },
            format="json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        record_id = create_response.data["id"]
        record = MedicalRecord.objects.get(pk=record_id)
        self.assertEqual(list(record.teeth.all()), [self.tooth])
        self.assertEqual(list(record.services.all()), [self.service])
        self.assertEqual(create_response.data["tooth_codes"], ["A01"])

        retrieve_response = self.client.get(f"/api/v1/medical-records/{record_id}/")
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data["diagnosis"], "Initial diagnosis")

        update_response = self.client.patch(
            f"/api/v1/medical-records/{record_id}/",
            {
                "diagnosis": "Updated diagnosis",
                "teeth": [],
                "services": [],
            },
            format="json",
        )

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        record.refresh_from_db()
        self.assertEqual(record.diagnosis, "Updated diagnosis")
        self.assertFalse(record.teeth.exists())
        self.assertFalse(record.services.exists())

    def test_medical_record_rejects_teeth_from_another_dentition(self):
        child_tooth = Tooth.objects.create(
            code="C01",
            dentition_type=Patient.CHILD,
            display_order=1,
        )

        response = self.client.post(
            "/api/v1/medical-records/",
            {
                "appointment": self.appointment.id,
                "diagnosis": "Diagnosis",
                "treatment_plan": "Plan",
                "teeth": [child_tooth.id],
                "services": [],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Selected teeth must match", str(response.data["teeth"]))
        self.assertFalse(MedicalRecord.objects.exists())

    def test_dentist_cannot_create_record_for_another_dentists_appointment(self):
        other_user = User.objects.create_user(username="other-record-dentist", password="test-pass")
        dentist_role = Role.objects.get(code="DENTIST")
        other_profile = ClinicUser.objects.create(user=other_user, role=dentist_role)
        other_doctor = Doctor.objects.create(
            clinic_user=other_profile,
            license_number="RECORD-TEST-002",
            specialization="General dentistry",
        )
        other_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=other_doctor,
            appointment_date=timezone.now() + timedelta(days=2),
            status=Appointment.Status.CONFIRMED,
        )

        response = self.client.post(
            "/api/v1/medical-records/",
            {
                "appointment": other_appointment.id,
                "diagnosis": "Diagnosis",
                "treatment_plan": "Plan",
                "teeth": [],
                "services": [],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("only document appointments assigned to you", str(response.data["appointment"]))
        self.assertFalse(MedicalRecord.objects.exists())
