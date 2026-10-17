from datetime import datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from appointments.models import Appointment as ScheduledAppointment, MedicalRecord
from .models import ClinicUser, Doctor, Invoice, InvoiceItem, Patient, Role, Service, Tooth

User = get_user_model()


@override_settings(ALLOWED_HOSTS=["testserver"])
class AuthenticationAndManagementApiTests(APITestCase):
    def setUp(self):
        self.admin_role = Role.objects.create(code="ADMIN", name="Administrator")
        self.dentist_role = Role.objects.create(code="DENTIST", name="Dentist")
        self.admin = User.objects.create_user(username="clinic-admin", password="AdminPass123!")
        self.dentist = User.objects.create_user(
            username="clinic-dentist",
            password="DentistPass123!",
            first_name="Thu",
            last_name="Uyên",
        )
        ClinicUser.objects.create(user=self.admin, role=self.admin_role)
        dentist_profile = ClinicUser.objects.create(user=self.dentist, role=self.dentist_role, phone="0901234567")
        Doctor.objects.create(
            clinic_user=dentist_profile,
            license_number="DMS-TEST-001",
            specialization="General dentistry",
        )
        self.patient = Patient.objects.create(patient_code="DMS-TEST-001", full_name="Test Patient")
        self.service = Service.objects.create(code="CHECKUP", name="Dental check-up", price="250000", duration_minutes=30)

    def authenticate(self, username, password):
        response = self.client.post(
            reverse("token"),
            {"username": username, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_business_apis_require_authentication(self):
        response = self.client.get("/api/v1/services/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_returns_token_and_current_user_profile(self):
        self.authenticate("clinic-admin", "AdminPass123!")
        response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], "ADMIN")
        self.assertEqual(response.data["username"], "clinic-admin")

    def test_legacy_admin_role_without_clinic_profile_does_not_unlock_admin_menu(self):
        User.objects.create_user(
            username="unassigned-admin",
            password="AdminPass123!",
            role=User.Role.ADMIN,
        )
        self.authenticate("unassigned-admin", "AdminPass123!")
        response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], "RECEPTIONIST")

    def test_admin_can_manage_services_and_authenticated_user_can_read_doctors(self):
        self.authenticate("clinic-admin", "AdminPass123!")
        created = self.client.post(
            "/api/v1/services/",
            {
                "code": "CLEAN",
                "name": "Cleaning",
                "description": "",
                "price": "500000.00",
                "duration_minutes": 45,
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        updated = self.client.patch(
            f"/api/v1/services/{created.data['id']}/",
            {"price": "600000.00"},
            format="json",
        )
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.assertEqual(updated.data["price"], "600000.00")
        doctors = self.client.get("/api/v1/doctors/")
        self.assertEqual(doctors.status_code, status.HTTP_200_OK)
        self.assertEqual(doctors.data[0]["full_name"], "Thu Uyên")

    def test_patient_profile_api_creates_and_returns_full_patient_details(self):
        self.authenticate("clinic-admin", "AdminPass123!")
        created = self.client.post(
            "/api/v1/patients/",
            {
                "patient_code": "DMS-FULL-001",
                "full_name": "Full Profile Patient",
                "phone": "0900000000",
                "date_of_birth": "1990-05-21",
                "dentition_type": "ADULT",
                "medical_history": "Hypertension",
                "allergies": "Penicillin",
            },
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.data["date_of_birth"], "1990-05-21")
        self.assertEqual(created.data["medical_history"], "Hypertension")
        listed = self.client.get("/api/v1/patients/")
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual(listed.data[0]["patient_code"], "DMS-FULL-001")

    def test_patient_search_matches_patient_code_name_and_phone(self):
        self.authenticate("clinic-admin", "AdminPass123!")
        Patient.objects.create(
            patient_code="DMS-SEARCH-02",
            full_name="Nguyen Thi Binh",
            phone="0912345678",
        )
        for query in ("DMS-SEARCH-02", "thi binh", "12345678"):
            with self.subTest(query=query):
                response = self.client.get("/api/v1/patients/", {"search": query})
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(len(response.data), 1)
                self.assertEqual(response.data[0]["patient_code"], "DMS-SEARCH-02")

    def test_patient_search_returns_empty_list_when_no_match(self):
        self.authenticate("clinic-admin", "AdminPass123!")
        response = self.client.get(
            "/api/v1/patients/", {"search": "UNKNOWN-IDENTIFIER"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_patient_search_rejects_blank_or_invalid_terms(self):
        self.authenticate("clinic-admin", "AdminPass123!")
        for query in ("   ", "%%%", "A" * 101):
            with self.subTest(query=query):
                response = self.client.get("/api/v1/patients/", {"search": query})
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("search", response.data)

    def test_dentist_cannot_write_service_catalog(self):
        self.authenticate("clinic-dentist", "DentistPass123!")
        response = self.client.post(
            "/api/v1/services/",
            {
                "code": "RESTRICTED",
                "name": "Restricted",
                "price": "100000",
                "duration_minutes": 20,
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_dentist_cannot_register_patients_from_reception_screen(self):
        self.authenticate("clinic-dentist", "DentistPass123!")
        response = self.client.post(
            "/api/v1/patients/",
            {"patient_code": "DMS-DENTIST-001", "full_name": "Unauthorized Intake"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_deleting_service_deactivates_it_to_preserve_references(self):
        self.authenticate("clinic-admin", "AdminPass123!")
        service = Service.objects.get(code="CHECKUP")
        invoice = Invoice.objects.create(
            patient=self.patient,
            invoice_number="INV-TEST-001",
            total_amount="250000.00",
            paid_amount="0",
            status=Invoice.ISSUED,
        )
        InvoiceItem.objects.create(
            invoice=invoice,
            service=service,
            description=service.name,
            quantity=1,
            unit_price=service.price,
        )
        response = self.client.delete(f"/api/v1/services/{service.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        service.refresh_from_db()
        self.assertFalse(service.is_active)

    def create_medical_record(self, services):
        appointment = ScheduledAppointment.objects.create(
            patient=self.patient,
            doctor=Doctor.objects.get(license_number="DMS-TEST-001"),
            service=self.service,
            appointment_date=timezone.now() + timedelta(days=1),
        )
        record = MedicalRecord.objects.create(
            appointment=appointment,
            diagnosis="Test diagnosis",
            treatment_plan="Test plan",
        )
        record.services.set(services)
        return record

    def invoice_payload(self, record, items):
        return {"medical_record": record.id, "items": items}

    def test_invoice_for_one_prescribed_service_uses_catalog_price_and_sets_unpaid_status(self):
        record = self.create_medical_record([self.service])
        self.authenticate("clinic-admin", "AdminPass123!")

        response = self.client.post(
            "/api/v1/invoices/",
            self.invoice_payload(
                record,
                [{"service": self.service.id, "quantity": 1, "unit_price": "1", "amount": "1"}],
            ),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["patient"], self.patient.id)
        self.assertEqual(response.data["medical_record"], record.id)
        self.assertEqual(response.data["total_amount"], "250000.00")
        self.assertEqual(response.data["paid_amount"], "0.00")
        self.assertEqual(response.data["balance"], "250000.00")
        self.assertEqual(response.data["status"], Invoice.ISSUED)
        self.assertTrue(response.data["invoice_number"].startswith("INV-"))
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(response.data["items"][0]["unit_price"], "250000.00")
        self.assertEqual(response.data["items"][0]["amount"], "250000.00")

    def test_invoice_calculates_multiple_services_and_quantities_exactly(self):
        second_service = Service.objects.create(
            code="FILLING",
            name="Filling",
            price="125000.25",
            duration_minutes=40,
        )
        record = self.create_medical_record([self.service, second_service])
        self.authenticate("clinic-admin", "AdminPass123!")

        response = self.client.post(
            "/api/v1/invoices/",
            self.invoice_payload(
                record,
                [
                    {"service": self.service.id, "quantity": 2},
                    {"service": second_service.id, "quantity": 3},
                ],
            ),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        amounts = [Decimal(item["amount"]) for item in response.data["items"]]
        self.assertEqual(amounts, [Decimal("500000.00"), Decimal("375000.75")])
        self.assertEqual(Decimal(response.data["total_amount"]), sum(amounts))
        self.assertEqual(Decimal(response.data["total_amount"]), Decimal("875000.75"))

    def test_invoice_rejects_empty_prescribed_services_and_empty_item_list(self):
        empty_record = self.create_medical_record([])
        self.authenticate("clinic-admin", "AdminPass123!")

        empty_record_response = self.client.post(
            "/api/v1/invoices/",
            self.invoice_payload(empty_record, []),
            format="json",
        )
        self.assertEqual(empty_record_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("medical_record", empty_record_response.data)

        prescribed_record = self.create_medical_record([self.service])
        empty_items_response = self.client.post(
            "/api/v1/invoices/",
            self.invoice_payload(prescribed_record, []),
            format="json",
        )
        self.assertEqual(empty_items_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Invoice.objects.count(), 0)

    def test_invoice_rejects_negative_catalog_price_and_invalid_quantity(self):
        record = self.create_medical_record([self.service])
        self.authenticate("clinic-admin", "AdminPass123!")
        self.service.price = "-1.00"
        self.service.save(update_fields=["price"])

        invalid_price = self.client.post(
            "/api/v1/invoices/",
            self.invoice_payload(record, [{"service": self.service.id, "quantity": 1}]),
            format="json",
        )
        self.assertEqual(invalid_price.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price or line total", str(invalid_price.data))

        self.service.price = "250000.00"
        self.service.save(update_fields=["price"])
        invalid_quantity = self.client.post(
            "/api/v1/invoices/",
            self.invoice_payload(record, [{"service": self.service.id, "quantity": 0}]),
            format="json",
        )
        self.assertEqual(invalid_quantity.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Invoice.objects.count(), 0)

        self.service.price = "9999999999.99"
        self.service.save(update_fields=["price"])
        overflow = self.client.post(
            "/api/v1/invoices/",
            self.invoice_payload(record, [{"service": self.service.id, "quantity": 2}]),
            format="json",
        )
        self.assertEqual(overflow.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("supported range", str(overflow.data))
        self.assertEqual(Invoice.objects.count(), 0)

    def test_invoice_rejects_unprescribed_services_and_duplicate_service_rows(self):
        another_service = Service.objects.create(
            code="XRAY",
            name="X-ray",
            price="150000",
            duration_minutes=15,
        )
        record = self.create_medical_record([self.service])
        self.authenticate("clinic-admin", "AdminPass123!")

        unprescribed = self.client.post(
            "/api/v1/invoices/",
            self.invoice_payload(record, [{"service": another_service.id, "quantity": 1}]),
            format="json",
        )
        self.assertEqual(unprescribed.status_code, status.HTTP_400_BAD_REQUEST)

        duplicate_rows = self.client.post(
            "/api/v1/invoices/",
            self.invoice_payload(
                record,
                [
                    {"service": self.service.id, "quantity": 1},
                    {"service": self.service.id, "quantity": 2},
                ],
            ),
            format="json",
        )
        self.assertEqual(duplicate_rows.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Invoice.objects.count(), 0)

    def test_invoice_cannot_be_created_twice_for_same_medical_record(self):
        record = self.create_medical_record([self.service])
        self.authenticate("clinic-admin", "AdminPass123!")
        payload = self.invoice_payload(record, [{"service": self.service.id, "quantity": 1}])

        first = self.client.post("/api/v1/invoices/", payload, format="json")
        second = self.client.post("/api/v1/invoices/", payload, format="json")

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already exists", str(second.data["medical_record"]))
        self.assertEqual(Invoice.objects.count(), 1)

    def test_receptionist_can_see_only_billing_fields_for_available_records(self):
        record = self.create_medical_record([self.service])
        receptionist_role = Role.objects.create(code="RECEPTIONIST", name="Receptionist")
        receptionist = User.objects.create_user(username="invoice-receptionist", password="Reception123!")
        ClinicUser.objects.create(user=receptionist, role=receptionist_role)
        self.client.force_authenticate(receptionist)

        response = self.client.get("/api/v1/invoices/available-records/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], record.id)
        self.assertEqual(response.data[0]["patient_name"], self.patient.full_name)
        self.assertEqual(response.data[0]["services"][0]["price"], "250000.00")
        self.assertNotIn("diagnosis", response.data[0])
        created = self.client.post(
            "/api/v1/invoices/",
            self.invoice_payload(record, [{"service": self.service.id, "quantity": 2}]),
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.data["total_amount"], "500000.00")
        self.assertEqual(self.client.get("/api/v1/invoices/available-records/").data, [])

    def test_dentist_cannot_access_invoice_endpoints(self):
        self.authenticate("clinic-dentist", "DentistPass123!")

        response = self.client.get("/api/v1/invoices/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_health_check_remains_public(self):
        response = self.client.get("/api/v1/health/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reception_can_book_within_a_dentist_shift_and_overlaps_are_rejected(self):
        work_date = timezone.localdate() + timedelta(days=3)
        self.authenticate("clinic-admin", "AdminPass123!")
        doctor_id = Doctor.objects.get(license_number="DMS-TEST-001").id
        shift = self.client.post(
            "/api/v1/schedules/",
            {
                "doctor": doctor_id,
                "work_date": work_date.isoformat(),
                "start_time": "09:00",
                "end_time": "12:00",
            },
            format="json",
        )
        self.assertEqual(shift.status_code, status.HTTP_201_CREATED)
        appointment_date = timezone.make_aware(datetime.combine(work_date, time(9, 0)))
        payload = {
            "patient": self.patient.id,
            "doctor": doctor_id,
            "service": self.service.id,
            "appointment_date": appointment_date.isoformat(),
            "notes": "Routine dental check-up",
        }
        created = self.client.post("/api/v1/appointments/", payload, format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.data["patient_name"], self.patient.full_name)
        self.assertEqual(created.data["service_name"], self.service.name)
        self.assertEqual(created.data["notes"], "Routine dental check-up")
        payload["appointment_date"] = timezone.make_aware(
            datetime.combine(work_date, time(9, 15))
        ).isoformat()
        overlap = self.client.post("/api/v1/appointments/", payload, format="json")
        self.assertEqual(overlap.status_code, status.HTTP_400_BAD_REQUEST)

    def test_appointment_rejects_missing_required_fields(self):
        self.authenticate("clinic-admin", "AdminPass123!")
        response = self.client.post("/api/v1/appointments/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_appointment_rejects_time_without_a_matching_work_shift(self):
        self.authenticate("clinic-admin", "AdminPass123!")
        appointment_date = timezone.make_aware(
            datetime.combine(timezone.localdate() + timedelta(days=5), time(9, 0))
        )
        response = self.client.post(
            "/api/v1/appointments/",
            {
                "patient": self.patient.id,
                "doctor": Doctor.objects.get(license_number="DMS-TEST-001").id,
                "service": self.service.id,
                "appointment_date": appointment_date.isoformat(),
                "notes": "Tooth pain",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_receptionist_can_manage_shifts_and_book_appointments(self):
        receptionist_role = Role.objects.create(code="RECEPTIONIST", name="Receptionist")
        receptionist = User.objects.create_user(username="front-desk", password="ReceptionPass123!")
        ClinicUser.objects.create(user=receptionist, role=receptionist_role)
        self.client.force_authenticate(receptionist)
        patient = self.client.post(
            "/api/v1/patients/",
            {"patient_code": "DMS-RECEPTION-001", "full_name": "Front Desk Patient"},
            format="json",
        )
        self.assertEqual(patient.status_code, status.HTTP_201_CREATED)
        work_date = timezone.localdate() + timedelta(days=4)
        shift = self.client.post(
            "/api/v1/schedules/",
            {
                "doctor": Doctor.objects.get(license_number="DMS-TEST-001").id,
                "work_date": work_date.isoformat(),
                "start_time": "10:00",
                "end_time": "11:00",
            },
            format="json",
        )
        self.assertEqual(shift.status_code, status.HTTP_201_CREATED)
        appointment = self.client.post(
            "/api/v1/appointments/",
            {
                "patient": self.patient.id,
                "doctor": Doctor.objects.get(license_number="DMS-TEST-001").id,
                "service": self.service.id,
                "appointment_date": timezone.make_aware(
                    datetime.combine(work_date, time(10, 0))
                ).isoformat(),
            },
            format="json",
        )
        self.assertEqual(appointment.status_code, status.HTTP_201_CREATED)

    def test_dentist_can_save_emr_teeth_and_prescribed_services_for_own_visit(self):
        doctor = Doctor.objects.get(license_number="DMS-TEST-001")
        appointment = ScheduledAppointment.objects.create(
            patient=self.patient,
            doctor=doctor,
            service=self.service,
            appointment_date=timezone.now() + timedelta(days=1),
        )
        tooth = Tooth.objects.create(code="A01", dentition_type=Patient.ADULT, display_order=1)
        self.authenticate("clinic-dentist", "DentistPass123!")
        response = self.client.post(
            "/api/v1/medical-records/",
            {
                "appointment": appointment.id,
                "diagnosis": "Caries on upper incisor",
                "treatment_plan": "Restore and review",
                "prescription": "",
                "notes": "Follow-up in two weeks",
                "teeth": [tooth.id],
                "services": [self.service.id],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tooth_codes"], ["A01"])
        self.assertEqual(response.data["services"], [self.service.id])
