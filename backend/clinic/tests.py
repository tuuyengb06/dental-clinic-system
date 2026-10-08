from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import ClinicUser, Doctor, InvoiceItem, Patient, Role, Service


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
        Service.objects.create(code="CHECKUP", name="Dental check-up", price="250000", duration_minutes=30)

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

    def test_deleting_service_deactivates_it_to_preserve_references(self):
        self.authenticate("clinic-admin", "AdminPass123!")
        service = Service.objects.get(code="CHECKUP")
        created_invoice = self.client.post(
            "/api/v1/invoices/",
            {
                "patient": self.patient.id,
                "invoice_number": "INV-TEST-001",
                "total_amount": "250000.00",
                "paid_amount": "0",
                "status": "ISSUED",
            },
            format="json",
        )
        self.assertEqual(created_invoice.status_code, status.HTTP_201_CREATED)
        InvoiceItem.objects.create(
            invoice_id=created_invoice.data["id"],
            service=service,
            description=service.name,
            quantity=1,
            unit_price=service.price,
        )
        response = self.client.delete(f"/api/v1/services/{service.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        service.refresh_from_db()
        self.assertFalse(service.is_active)

    def test_health_check_remains_public(self):
        response = self.client.get("/api/v1/health/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
