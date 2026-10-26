from datetime import date, datetime, time, timedelta
from decimal import Decimal
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.db import DatabaseError, IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from appointments.models import Appointment as ScheduledAppointment, MedicalRecord
from .models import (
    ActiveInvoicePayment,
    BankTransferVerification,
    ClinicUser,
    Doctor,
    Invoice,
    InvoiceItem,
    Patient,
    Payment,
    Radiograph,
    Role,
    Service,
    Tooth,
)

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
        self.doctor = Doctor.objects.create(
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

    def test_dentist_patient_list_contains_only_assigned_patients(self):
        other_patient = Patient.objects.create(
            patient_code="DMS-OTHER-001",
            full_name="Other Patient",
        )
        ScheduledAppointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
        )
        self.authenticate("clinic-dentist", "DentistPass123!")

        response = self.client.get("/api/v1/patients/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({item["id"] for item in response.data}, {self.patient.pk})
        self.assertNotIn(other_patient.pk, {item["id"] for item in response.data})

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

    def create_issued_invoice(
        self,
        total="250000.00",
        paid="0.00",
        invoice_status=Invoice.ISSUED,
    ):
        return Invoice.objects.create(
            patient=self.patient,
            invoice_number=f"INV-PAY-TEST-{Invoice.objects.count() + 1:03d}",
            total_amount=total,
            paid_amount=paid,
            status=invoice_status,
        )

    def pay_cash(self, invoice_id, method=Payment.CASH):
        return self.client.post(
            f"/api/v1/invoices/{invoice_id}/pay-cash/",
            {"method": method},
            format="json",
        )

    def pay_qr(self, invoice_id, data=None):
        return self.client.post(
            f"/api/v1/invoices/{invoice_id}/pay-qr/",
            data or {},
            format="json",
        )

    def reconcile_qr(self, invoice_id, reference="BANK-TXN-001", amount="250000.00", verified=True):
        return self.client.post(
            f"/api/v1/invoices/{invoice_id}/reconcile-qr/",
            {
                "bank_reference": reference,
                "verified_amount": amount,
                "verified": verified,
            },
            format="json",
        )

    def cancel_qr(self, invoice_id, checked_no_payment=True):
        return self.client.post(
            f"/api/v1/invoices/{invoice_id}/cancel-qr/",
            {"checked_no_payment": checked_no_payment},
            format="json",
        )

    def create_pending_qr_payment(self, invoice):
        payment = Payment.objects.create(
            invoice=invoice,
            amount=invoice.total_amount,
            method=Payment.BANK_TRANSFER,
            status=Payment.PENDING,
            bank_id="MB",
            bank_account_number="0123456789",
            bank_account_name="LOTUS DENTAL",
        )
        ActiveInvoicePayment.objects.create(invoice=invoice, payment=payment)
        return payment

    def test_receptionist_can_pay_full_invoice_in_cash(self):
        receptionist_role = Role.objects.create(code="RECEPTIONIST", name="Receptionist")
        receptionist = User.objects.create_user(username="cash-receptionist", password="Reception123!")
        receptionist_profile = ClinicUser.objects.create(user=receptionist, role=receptionist_role)
        invoice = self.create_issued_invoice(total="250000.75")
        self.client.force_authenticate(receptionist)

        response = self.pay_cash(invoice.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Invoice.PAID)
        self.assertEqual(response.data["paid_amount"], "250000.75")
        self.assertEqual(response.data["balance"], "0.00")
        self.assertEqual(len(response.data["payments"]), 1)
        payment_data = response.data["payments"][0]
        self.assertEqual(payment_data["amount"], "250000.75")
        self.assertEqual(payment_data["method"], Payment.CASH)
        self.assertEqual(payment_data["status"], Payment.COMPLETED)
        self.assertEqual(payment_data["received_by_name"], receptionist.get_username())
        self.assertTrue(payment_data["paid_at"])
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.PAID)
        self.assertEqual(invoice.paid_amount, invoice.total_amount)
        payment = Payment.objects.get(invoice=invoice)
        self.assertEqual(payment.received_by, receptionist_profile)

    def test_paid_invoice_rejects_duplicate_cash_payment(self):
        invoice = self.create_issued_invoice()
        self.authenticate("clinic-admin", "AdminPass123!")

        first = self.pay_cash(invoice.id)
        duplicate = self.pay_cash(invoice.id)

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already been paid", str(duplicate.data["status"]))
        self.assertEqual(Payment.objects.filter(invoice=invoice).count(), 1)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.PAID)

    def test_cash_payment_rejects_missing_invoice(self):
        self.authenticate("clinic-admin", "AdminPass123!")

        response = self.pay_cash(99999)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Payment.objects.count(), 0)

    def test_cash_payment_rejects_zero_invalid_and_nonissued_invoices(self):
        zero_invoice = self.create_issued_invoice(total="0.00")
        invalid_balance_invoice = self.create_issued_invoice(total="250000.00", paid="1.00")
        draft_invoice = self.create_issued_invoice(total="250000.00", invoice_status=Invoice.DRAFT)
        self.authenticate("clinic-admin", "AdminPass123!")

        for invoice in (zero_invoice, invalid_balance_invoice, draft_invoice):
            with self.subTest(invoice=invoice.invoice_number):
                response = self.pay_cash(invoice.id)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Payment.objects.count(), 0)
        for invoice in (zero_invoice, invalid_balance_invoice, draft_invoice):
            invoice.refresh_from_db()
            expected_status = (
                Invoice.DRAFT if invoice == draft_invoice else Invoice.ISSUED
            )
            self.assertEqual(invoice.status, expected_status)

    def test_cash_payment_rejects_non_cash_method(self):
        invoice = self.create_issued_invoice()
        self.authenticate("clinic-admin", "AdminPass123!")

        response = self.pay_cash(invoice.id, method=Payment.CARD)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Payment.objects.count(), 0)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.ISSUED)

    def test_cash_payment_rejects_client_supplied_amount(self):
        invoice = self.create_issued_invoice()
        self.authenticate("clinic-admin", "AdminPass123!")

        response = self.client.post(
            f"/api/v1/invoices/{invoice.id}/pay-cash/",
            {"method": Payment.CASH, "amount": "-1.00"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("calculated by the server", str(response.data))
        self.assertEqual(Payment.objects.count(), 0)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.ISSUED)

    def test_payment_database_error_does_not_update_invoice(self):
        invoice = self.create_issued_invoice()
        self.authenticate("clinic-admin", "AdminPass123!")

        with patch("clinic.views.Payment.objects.create", side_effect=DatabaseError("write failed")):
            response = self.pay_cash(invoice.id)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("No changes were applied", response.data["detail"])
        self.assertEqual(Payment.objects.count(), 0)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.ISSUED)
        self.assertEqual(invoice.paid_amount, Decimal("0.00"))

    def test_unrelated_payment_integrity_error_is_reported_as_save_failure(self):
        invoice = self.create_issued_invoice()
        self.authenticate("clinic-admin", "AdminPass123!")

        with patch(
            "clinic.views.Payment.objects.create",
            side_effect=IntegrityError("unrelated constraint failure"),
        ):
            response = self.pay_cash(invoice.id)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("No changes were applied", response.data["detail"])
        self.assertEqual(Payment.objects.count(), 0)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.ISSUED)
        self.assertEqual(invoice.paid_amount, Decimal("0.00"))

    def test_dentist_cannot_record_cash_payment(self):
        invoice = self.create_issued_invoice()
        self.authenticate("clinic-dentist", "DentistPass123!")

        response = self.pay_cash(invoice.id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Payment.objects.count(), 0)

    @override_settings(
        VIETQR_BANK_ID="MB",
        VIETQR_ACCOUNT_NUMBER="0123456789",
        VIETQR_ACCOUNT_NAME="LOTUS DENTAL",
    )
    def test_receptionist_can_create_vietqr_and_invoice_stays_unpaid(self):
        receptionist_role = Role.objects.create(code="RECEPTIONIST", name="Receptionist")
        receptionist = User.objects.create_user(
            username="qr-receptionist",
            password="ReceptionPass123!",
        )
        ClinicUser.objects.create(user=receptionist, role=receptionist_role)
        invoice = self.create_issued_invoice(total="250000.00")
        self.client.force_authenticate(receptionist)

        response = self.pay_qr(invoice.id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["invoice"]["status"], Invoice.ISSUED)
        self.assertEqual(response.data["invoice"]["paid_amount"], "0.00")
        self.assertEqual(len(response.data["invoice"]["payments"]), 1)
        self.assertEqual(response.data["transfer"]["amount"], "250000.00")
        self.assertEqual(response.data["transfer"]["description"], invoice.invoice_number)
        self.assertEqual(response.data["transfer"]["status"], Payment.PENDING)
        parsed_qr = urlparse(response.data["transfer"]["qr_url"])
        self.assertEqual(parsed_qr.netloc, "img.vietqr.io")
        self.assertIn("/image/MB-0123456789-compact2.png", parsed_qr.path)
        self.assertEqual(
            parse_qs(parsed_qr.query),
            {
                "amount": ["250000"],
                "addInfo": [invoice.invoice_number],
                "accountName": ["LOTUS DENTAL"],
            },
        )

        invoice.refresh_from_db()
        payment = Payment.objects.get(invoice=invoice)
        self.assertEqual(payment.method, Payment.BANK_TRANSFER)
        self.assertEqual(payment.status, Payment.PENDING)
        self.assertEqual(payment.amount, invoice.total_amount)
        self.assertIsNone(payment.paid_at)
        self.assertEqual(invoice.status, Invoice.ISSUED)
        self.assertEqual(invoice.paid_amount, Decimal("0.00"))

    @override_settings(
        VIETQR_BANK_ID="MB",
        VIETQR_ACCOUNT_NUMBER="0123456789",
        VIETQR_ACCOUNT_NAME="LOTUS DENTAL",
    )
    def test_repeated_qr_request_reuses_pending_transaction(self):
        invoice = self.create_issued_invoice()
        self.authenticate("clinic-admin", "AdminPass123!")

        first = self.pay_qr(invoice.id)
        with self.settings(
            VIETQR_BANK_ID="VCB",
            VIETQR_ACCOUNT_NUMBER="9876543210",
            VIETQR_ACCOUNT_NAME="CHANGED ACCOUNT",
        ):
            second = self.pay_qr(invoice.id)

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertTrue(second.data["reused"])
        self.assertEqual(first.data["transfer"], second.data["transfer"])
        self.assertEqual(Payment.objects.filter(invoice=invoice).count(), 1)
        payment = Payment.objects.get(invoice=invoice)
        self.assertEqual(payment.bank_id, "MB")
        self.assertEqual(payment.bank_account_number, "0123456789")
        self.assertEqual(payment.bank_account_name, "LOTUS DENTAL")
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.ISSUED)
        self.assertEqual(invoice.paid_amount, Decimal("0.00"))

    def test_qr_payment_requires_valid_vietqr_configuration(self):
        invoice = self.create_issued_invoice()
        self.authenticate("clinic-admin", "AdminPass123!")

        with self.settings(
            VIETQR_BANK_ID="MB",
            VIETQR_ACCOUNT_NUMBER="invalid-account",
            VIETQR_ACCOUNT_NAME="LOTUS DENTAL",
        ):
            response = self.pay_qr(invoice.id)

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("VietQR is not configured", response.data["detail"])
        self.assertEqual(Payment.objects.count(), 0)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.ISSUED)

    @override_settings(
        VIETQR_BANK_ID="MB",
        VIETQR_ACCOUNT_NUMBER="0123456789",
        VIETQR_ACCOUNT_NAME="LOTUS DENTAL",
    )
    def test_qr_payment_rejects_fractional_amount_and_client_transfer_data(self):
        invoice = self.create_issued_invoice(total="250000.50")
        self.authenticate("clinic-admin", "AdminPass123!")

        fractional_amount = self.pay_qr(invoice.id)
        injected_amount = self.pay_qr(invoice.id, {"amount": "1"})

        self.assertEqual(fractional_amount.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("whole number of VND", str(fractional_amount.data))
        self.assertEqual(injected_amount.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("generated by the server", str(injected_amount.data))
        self.assertEqual(Payment.objects.count(), 0)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.ISSUED)

    @override_settings(
        VIETQR_BANK_ID="MB",
        VIETQR_ACCOUNT_NUMBER="0123456789",
        VIETQR_ACCOUNT_NAME="LOTUS DENTAL",
    )
    def test_qr_payment_rejects_missing_or_already_paid_invoice(self):
        paid_invoice = self.create_issued_invoice()
        self.authenticate("clinic-admin", "AdminPass123!")
        self.assertEqual(self.pay_cash(paid_invoice.id).status_code, status.HTTP_200_OK)

        missing = self.pay_qr(99999)
        paid = self.pay_qr(paid_invoice.id)

        self.assertEqual(missing.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(paid.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Payment.objects.filter(invoice=paid_invoice).count(), 1)
        paid_invoice.refresh_from_db()
        self.assertEqual(paid_invoice.status, Invoice.PAID)

    @override_settings(
        VIETQR_BANK_ID="MB",
        VIETQR_ACCOUNT_NUMBER="0123456789",
        VIETQR_ACCOUNT_NAME="LOTUS DENTAL",
    )
    def test_cash_payment_cannot_override_pending_qr_transfer(self):
        invoice = self.create_issued_invoice()
        self.authenticate("clinic-admin", "AdminPass123!")
        qr_response = self.pay_qr(invoice.id)

        cash_response = self.pay_cash(invoice.id)

        self.assertEqual(qr_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(cash_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already pending", str(cash_response.data["status"]))
        self.assertEqual(Payment.objects.filter(invoice=invoice).count(), 1)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.ISSUED)
        self.assertEqual(invoice.paid_amount, Decimal("0.00"))

    def test_admin_can_reconcile_matching_qr_transfer_with_auditable_reference(self):
        receptionist_role = Role.objects.create(code="RECEPTIONIST", name="Receptionist")
        receptionist = User.objects.create_user(
            username="qr-verifier",
            password="ReceptionPass123!",
        )
        ClinicUser.objects.create(user=receptionist, role=receptionist_role)
        invoice = self.create_issued_invoice()
        payment = self.create_pending_qr_payment(invoice)
        self.client.force_authenticate(receptionist)

        response = self.reconcile_qr(invoice.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Invoice.PAID)
        self.assertEqual(response.data["paid_amount"], "250000.00")
        payment_data = response.data["payments"][0]
        self.assertEqual(payment_data["status"], Payment.COMPLETED)
        self.assertEqual(payment_data["bank_reference"], "BANK-TXN-001")
        self.assertEqual(payment_data["verified_by_name"], "qr-verifier")
        self.assertTrue(payment_data["verified_at"])
        self.assertTrue(payment_data["paid_at"])
        verification = BankTransferVerification.objects.get(payment=payment)
        self.assertEqual(verification.reference, "BANK-TXN-001")
        self.assertEqual(verification.verified_by, receptionist)
        payment.refresh_from_db()
        invoice.refresh_from_db()
        self.assertEqual(payment.status, Payment.COMPLETED)
        self.assertEqual(invoice.status, Invoice.PAID)
        self.assertEqual(invoice.paid_amount, payment.amount)

    def test_qr_reconciliation_requires_staff_confirmation_and_exact_amount(self):
        invoice = self.create_issued_invoice()
        self.create_pending_qr_payment(invoice)
        self.client.force_authenticate(self.admin)

        unverified = self.reconcile_qr(invoice.id, verified=False)
        incorrect_amount = self.reconcile_qr(
            invoice.id,
            reference="BANK-TXN-WRONG-AMOUNT",
            amount="249999.00",
        )
        blank_reference = self.reconcile_qr(invoice.id, reference="   ")

        self.assertEqual(unverified.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(incorrect_amount.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(blank_reference.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(BankTransferVerification.objects.count(), 0)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.ISSUED)
        self.assertEqual(invoice.paid_amount, Decimal("0.00"))
        self.assertEqual(Payment.objects.get(invoice=invoice).status, Payment.PENDING)

    def test_qr_reconciliation_rejects_duplicate_reference_and_missing_pending_payment(self):
        first_invoice = self.create_issued_invoice()
        second_invoice = self.create_issued_invoice()
        self.create_pending_qr_payment(first_invoice)
        self.create_pending_qr_payment(second_invoice)
        self.client.force_authenticate(self.admin)

        first = self.reconcile_qr(first_invoice.id, reference="BANK-TXN-DUPLICATE")
        duplicate = self.reconcile_qr(second_invoice.id, reference="BANK-TXN-DUPLICATE")
        missing = self.reconcile_qr(99999, reference="BANK-TXN-MISSING")

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already been recorded", str(duplicate.data["bank_reference"]))
        self.assertEqual(missing.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(BankTransferVerification.objects.count(), 1)
        second_invoice.refresh_from_db()
        self.assertEqual(second_invoice.status, Invoice.ISSUED)

    def test_dentist_cannot_reconcile_qr_transfer(self):
        invoice = self.create_issued_invoice()
        self.create_pending_qr_payment(invoice)
        self.authenticate("clinic-dentist", "DentistPass123!")

        response = self.reconcile_qr(invoice.id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(BankTransferVerification.objects.count(), 0)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.ISSUED)

    def test_qr_reconciliation_database_error_rolls_back_all_changes(self):
        invoice = self.create_issued_invoice()
        payment = self.create_pending_qr_payment(invoice)
        self.client.force_authenticate(self.admin)

        with patch(
            "clinic.views.BankTransferVerification.objects.create",
            side_effect=DatabaseError("write failed"),
        ):
            response = self.reconcile_qr(invoice.id)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(BankTransferVerification.objects.count(), 0)
        payment.refresh_from_db()
        invoice.refresh_from_db()
        self.assertEqual(payment.status, Payment.PENDING)
        self.assertEqual(invoice.status, Invoice.ISSUED)
        self.assertEqual(invoice.paid_amount, Decimal("0.00"))

    def test_receptionist_can_cancel_pending_qr_after_checking_no_payment(self):
        receptionist_role = Role.objects.create(code="RECEPTIONIST", name="Receptionist")
        receptionist = User.objects.create_user(
            username="qr-canceller",
            password="ReceptionPass123!",
        )
        ClinicUser.objects.create(user=receptionist, role=receptionist_role)
        invoice = self.create_issued_invoice()
        payment = self.create_pending_qr_payment(invoice)
        self.client.force_authenticate(receptionist)

        response = self.cancel_qr(invoice.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Invoice.ISSUED)
        payment_data = response.data["payments"][0]
        self.assertEqual(payment_data["status"], Payment.CANCELLED)
        self.assertEqual(payment_data["cancelled_by_name"], "qr-canceller")
        self.assertTrue(payment_data["cancelled_at"])
        payment.refresh_from_db()
        invoice.refresh_from_db()
        self.assertEqual(payment.status, Payment.CANCELLED)
        self.assertEqual(payment.cancelled_by, receptionist)
        self.assertFalse(ActiveInvoicePayment.objects.filter(invoice=invoice).exists())
        self.assertEqual(invoice.status, Invoice.ISSUED)
        self.assertEqual(invoice.paid_amount, Decimal("0.00"))

    def test_qr_cancellation_requires_staff_to_confirm_account_was_checked(self):
        invoice = self.create_issued_invoice()
        payment = self.create_pending_qr_payment(invoice)
        self.client.force_authenticate(self.admin)

        response = self.cancel_qr(invoice.id, checked_no_payment=False)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.PENDING)

    def test_cancelled_qr_allows_cash_and_preserves_both_payment_records(self):
        invoice = self.create_issued_invoice()
        pending_payment = self.create_pending_qr_payment(invoice)
        self.client.force_authenticate(self.admin)

        cancelled = self.cancel_qr(invoice.id)
        cash_payment = self.pay_cash(invoice.id)

        self.assertEqual(cancelled.status_code, status.HTTP_200_OK)
        self.assertEqual(cash_payment.status_code, status.HTTP_200_OK)
        self.assertEqual(cash_payment.data["status"], Invoice.PAID)
        payment_rows = Payment.objects.filter(invoice=invoice).order_by("id")
        self.assertEqual(payment_rows.count(), 2)
        pending_payment.refresh_from_db()
        self.assertEqual(pending_payment.status, Payment.CANCELLED)
        self.assertEqual(payment_rows.last().method, Payment.CASH)
        self.assertEqual(payment_rows.last().status, Payment.COMPLETED)
        self.assertEqual(
            ActiveInvoicePayment.objects.get(invoice=invoice).payment_id,
            payment_rows.last().id,
        )

    @override_settings(
        VIETQR_BANK_ID="MB",
        VIETQR_ACCOUNT_NUMBER="0123456789",
        VIETQR_ACCOUNT_NAME="LOTUS DENTAL",
    )
    def test_cancelled_qr_allows_a_new_qr_attempt_without_losing_history(self):
        invoice = self.create_issued_invoice()
        old_payment = self.create_pending_qr_payment(invoice)
        self.authenticate("clinic-admin", "AdminPass123!")

        cancelled = self.cancel_qr(invoice.id)
        retried = self.pay_qr(invoice.id)

        self.assertEqual(cancelled.status_code, status.HTTP_200_OK)
        self.assertEqual(retried.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.filter(invoice=invoice).count(), 2)
        old_payment.refresh_from_db()
        self.assertEqual(old_payment.status, Payment.CANCELLED)
        self.assertEqual(retried.data["transfer"]["status"], Payment.PENDING)

    def test_cancelled_qr_cannot_be_reconciled_as_paid(self):
        invoice = self.create_issued_invoice()
        payment = self.create_pending_qr_payment(invoice)
        self.client.force_authenticate(self.admin)
        self.cancel_qr(invoice.id)

        response = self.reconcile_qr(invoice.id)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        payment.refresh_from_db()
        invoice.refresh_from_db()
        self.assertEqual(payment.status, Payment.CANCELLED)
        self.assertEqual(invoice.status, Invoice.ISSUED)

    @override_settings(
        VIETQR_BANK_ID="MB",
        VIETQR_ACCOUNT_NUMBER="0123456789",
        VIETQR_ACCOUNT_NAME="LOTUS DENTAL",
    )
    def test_qr_payment_database_error_does_not_change_invoice(self):
        invoice = self.create_issued_invoice()
        self.authenticate("clinic-admin", "AdminPass123!")

        with patch("clinic.views.Payment.objects.create", side_effect=DatabaseError("write failed")):
            response = self.pay_qr(invoice.id)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("No changes were applied", response.data["detail"])
        self.assertEqual(Payment.objects.count(), 0)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.ISSUED)
        self.assertEqual(invoice.paid_amount, Decimal("0.00"))

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


@override_settings(ALLOWED_HOSTS=["testserver"])
class RevenueVisitDashboardApiTests(APITestCase):
    def setUp(self):
        self.admin_role = Role.objects.create(code="ADMIN", name="Administrator")
        self.receptionist_role = Role.objects.create(code="RECEPTIONIST", name="Receptionist")
        self.admin = User.objects.create_user(
            username="dashboard-admin",
            password="DashboardPass123!",
        )
        self.receptionist = User.objects.create_user(
            username="dashboard-receptionist",
            password="DashboardPass123!",
        )
        ClinicUser.objects.create(user=self.admin, role=self.admin_role)
        ClinicUser.objects.create(user=self.receptionist, role=self.receptionist_role)
        dentist_role = Role.objects.create(code="DENTIST", name="Dentist")
        dentist_user = User.objects.create_user(
            username="dashboard-dentist",
            password="DashboardPass123!",
        )
        dentist_profile = ClinicUser.objects.create(user=dentist_user, role=dentist_role)
        self.doctor = Doctor.objects.create(
            clinic_user=dentist_profile,
            license_number="DASHBOARD-TEST-001",
        )
        self.patient = Patient.objects.create(
            patient_code="DASHBOARD-TEST-001",
            full_name="Dashboard Test Patient",
        )
        self.service = Service.objects.create(
            code="DASHBOARD-CHECKUP",
            name="Dashboard check-up",
            price="250000.00",
        )

    def dashboard(self, start_date, end_date, group_by="auto"):
        return self.client.get(
            "/api/v1/dashboard/analytics/",
            {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "group_by": group_by,
            },
        )

    def create_invoice(self, day, number, total, invoice_status):
        invoice = Invoice.objects.create(
            patient=self.patient,
            invoice_number=number,
            total_amount=total,
            paid_amount=total if invoice_status == Invoice.PAID else Decimal("0.00"),
            status=invoice_status,
        )
        issued_at = timezone.make_aware(datetime.combine(day, time(12, 0)))
        Invoice.objects.filter(pk=invoice.pk).update(issued_at=issued_at)
        return invoice

    def test_admin_dashboard_sums_paid_invoices_once_and_completed_visits(self):
        start_date = timezone.localdate() - timedelta(days=5)
        paid_invoice = self.create_invoice(
            start_date,
            "INV-DASHBOARD-PAID",
            Decimal("300000.00"),
            Invoice.PAID,
        )
        InvoiceItem.objects.create(
            invoice=paid_invoice,
            service=self.service,
            description="First service line",
            quantity=1,
            unit_price=Decimal("100000.00"),
        )
        InvoiceItem.objects.create(
            invoice=paid_invoice,
            service=self.service,
            description="Second service line",
            quantity=2,
            unit_price=Decimal("100000.00"),
        )
        Payment.objects.create(
            invoice=paid_invoice,
            amount=Decimal("300000.00"),
            method=Payment.CASH,
            status=Payment.COMPLETED,
        )
        pending_invoice = self.create_invoice(
            start_date + timedelta(days=1),
            "INV-DASHBOARD-ISSUED",
            Decimal("900000.00"),
            Invoice.ISSUED,
        )
        Payment.objects.create(
            invoice=pending_invoice,
            amount=Decimal("900000.00"),
            method=Payment.BANK_TRANSFER,
            status=Payment.PENDING,
        )
        appointment_date = timezone.make_aware(datetime.combine(start_date, time(9, 0)))
        ScheduledAppointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            service=self.service,
            appointment_date=appointment_date,
            status=ScheduledAppointment.Status.COMPLETED,
        )
        ScheduledAppointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            service=self.service,
            appointment_date=appointment_date + timedelta(days=1),
            status=ScheduledAppointment.Status.CONFIRMED,
        )
        ScheduledAppointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            service=self.service,
            appointment_date=appointment_date + timedelta(days=2),
            status=ScheduledAppointment.Status.CANCELLED,
        )
        self.client.force_authenticate(self.admin)

        response = self.dashboard(start_date, start_date + timedelta(days=3))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["group_by"], "day")
        self.assertEqual(response.data["timezone"], "Asia/Ho_Chi_Minh")
        self.assertEqual(response.data["revenue_definition"], "PAID invoice total_amount grouped by invoice issued_at.")
        self.assertEqual(response.data["visit_definition"], "Completed appointments grouped by appointment_date.")
        self.assertEqual(response.data["total_revenue"], "300000.00")
        self.assertEqual(response.data["total_visits"], 1)
        self.assertEqual(len(response.data["series"]), 4)
        self.assertEqual(
            response.data["series"],
            [
                {"period": start_date.isoformat(), "revenue": "300000.00", "visits": 1},
                {"period": (start_date + timedelta(days=1)).isoformat(), "revenue": "0.00", "visits": 0},
                {"period": (start_date + timedelta(days=2)).isoformat(), "revenue": "0.00", "visits": 0},
                {"period": (start_date + timedelta(days=3)).isoformat(), "revenue": "0.00", "visits": 0},
            ],
        )

    def test_admin_dashboard_groups_long_ranges_by_month_and_includes_empty_months(self):
        start_date = date(2026, 1, 20)
        end_date = date(2026, 4, 25)
        self.client.force_authenticate(self.admin)

        response = self.dashboard(start_date, end_date)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["group_by"], "month")
        self.assertEqual(response.data["total_revenue"], "0.00")
        self.assertEqual(response.data["total_visits"], 0)
        self.assertEqual(
            [item["period"] for item in response.data["series"]],
            ["2026-01", "2026-02", "2026-03", "2026-04"],
        )
        self.assertTrue(all(item["revenue"] == "0.00" and item["visits"] == 0 for item in response.data["series"]))

    def test_dashboard_rejects_invalid_ranges_and_grouping(self):
        self.client.force_authenticate(self.admin)
        today = timezone.localdate()
        reversed_range = self.dashboard(today, today - timedelta(days=1))
        invalid_date = self.client.get(
            "/api/v1/dashboard/analytics/",
            {"start_date": "not-a-date", "end_date": today.isoformat()},
        )
        too_many_daily_points = self.dashboard(today - timedelta(days=366), today, "day")
        invalid_grouping = self.dashboard(today, today, "week")

        self.assertEqual(reversed_range.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(invalid_date.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(too_many_daily_points.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(invalid_grouping.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dashboard_is_only_available_to_admins(self):
        today = timezone.localdate()
        anonymous = self.dashboard(today, today)
        self.client.force_authenticate(self.receptionist)
        receptionist = self.dashboard(today, today)
        self.client.force_authenticate(self.admin)
        admin = self.dashboard(today, today)

        self.assertEqual(anonymous.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(receptionist.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(admin.status_code, status.HTTP_200_OK)

class RadiographApiTests(APITestCase):
    def setUp(self):
        self.media_directory = TemporaryDirectory()
        self.addCleanup(self.media_directory.cleanup)
        self.media_settings = override_settings(MEDIA_ROOT=self.media_directory.name)
        self.media_settings.enable()
        self.addCleanup(self.media_settings.disable)

        admin_role = Role.objects.create(code="ADMIN", name="Administrator")
        dentist_role = Role.objects.create(code="DENTIST", name="Dentist")
        receptionist_role = Role.objects.create(code="RECEPTIONIST", name="Receptionist")
        self.admin = User.objects.create_user(
            username="radiograph-admin",
            password="RadiographPass123!",
        )
        self.dentist = User.objects.create_user(
            username="radiograph-dentist",
            password="RadiographPass123!",
        )
        self.receptionist = User.objects.create_user(
            username="radiograph-receptionist",
            password="RadiographPass123!",
        )
        ClinicUser.objects.create(user=self.admin, role=admin_role)
        dentist_profile = ClinicUser.objects.create(user=self.dentist, role=dentist_role)
        ClinicUser.objects.create(user=self.receptionist, role=receptionist_role)
        self.doctor = Doctor.objects.create(
            clinic_user=dentist_profile,
            license_number="RAD-TEST-001",
        )
        self.patient = Patient.objects.create(
            patient_code="RAD-PATIENT-001",
            full_name="Radiograph Patient",
        )
        self.other_patient = Patient.objects.create(
            patient_code="RAD-PATIENT-002",
            full_name="Unassigned Patient",
        )
        ScheduledAppointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
        )

    @staticmethod
    def png_file(name="xray.png", content=None):
        return SimpleUploadedFile(
            name,
            content or b"\x89PNG\r\n\x1a\n" + b"\x00" * 16,
            content_type="image/png",
        )

    def test_dentist_uploads_and_retrieves_assigned_patient_image(self):
        self.client.force_authenticate(self.dentist)
        uploaded = self.client.post(
            "/api/v1/radiographs/",
            {"patient": self.patient.pk, "image": self.png_file()},
            format="multipart",
        )

        self.assertEqual(uploaded.status_code, status.HTTP_201_CREATED)
        self.assertEqual(uploaded.data["content_type"], "image/png")
        self.assertEqual(uploaded.data["original_filename"], "xray.png")
        self.assertEqual(uploaded.data["file_size"], 24)
        self.assertNotIn("image", uploaded.data)

        listed = self.client.get(
            "/api/v1/radiographs/",
            {"patient": self.patient.pk},
        )
        image = self.client.get(
            f"/api/v1/radiographs/{uploaded.data['id']}/image/"
        )
        image_content = b"".join(image.streaming_content)

        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual(len(listed.data), 1)
        self.assertEqual(image.status_code, status.HTTP_200_OK)
        self.assertEqual(image["Content-Type"], "image/png")
        self.assertEqual(image["Cache-Control"], "private, no-store")
        self.assertEqual(image["X-Content-Type-Options"], "nosniff")
        self.assertTrue(image_content.startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertEqual(Radiograph.objects.count(), 1)

    def test_upload_rejects_wrong_format_mismatch_and_oversized_file(self):
        self.client.force_authenticate(self.admin)
        wrong_format = self.client.post(
            "/api/v1/radiographs/",
            {
                "patient": self.patient.pk,
                "image": self.png_file("xray.jpg"),
            },
            format="multipart",
        )
        unsupported = self.client.post(
            "/api/v1/radiographs/",
            {
                "patient": self.patient.pk,
                "image": self.png_file("scan.dcm"),
            },
            format="multipart",
        )
        oversized = self.client.post(
            "/api/v1/radiographs/",
            {
                "patient": self.patient.pk,
                "image": self.png_file(
                    content=b"\x89PNG\r\n\x1a\n" + b"\x00" * (10 * 1024 * 1024)
                ),
            },
            format="multipart",
        )

        self.assertEqual(wrong_format.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(unsupported.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(oversized.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Radiograph.objects.count(), 0)

    def test_dentist_cannot_access_unassigned_patient_image(self):
        self.client.force_authenticate(self.dentist)

        response = self.client.post(
            "/api/v1/radiographs/",
            {"patient": self.other_patient.pk, "image": self.png_file()},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Radiograph.objects.count(), 0)

    def test_dentist_cannot_retrieve_unassigned_patient_image(self):
        self.client.force_authenticate(self.admin)
        uploaded = self.client.post(
            "/api/v1/radiographs/",
            {"patient": self.other_patient.pk, "image": self.png_file()},
            format="multipart",
        )
        self.client.force_authenticate(self.dentist)

        response = self.client.get(
            f"/api/v1/radiographs/{uploaded.data['id']}/image/"
        )

        self.assertEqual(uploaded.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_receptionist_cannot_access_radiographs(self):
        self.client.force_authenticate(self.receptionist)

        listed = self.client.get("/api/v1/radiographs/")
        uploaded = self.client.post(
            "/api/v1/radiographs/",
            {"patient": self.patient.pk, "image": self.png_file()},
            format="multipart",
        )

        self.assertEqual(listed.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(uploaded.status_code, status.HTTP_403_FORBIDDEN)
