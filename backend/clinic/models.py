from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Role(models.Model):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ClinicUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="clinic_profile")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="users")
    phone = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Doctor(models.Model):
    clinic_user = models.OneToOneField(ClinicUser, on_delete=models.CASCADE, related_name="doctor_profile")
    license_number = models.CharField(max_length=40, unique=True)
    specialization = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return str(self.clinic_user)


class Patient(models.Model):
    ADULT = "ADULT"
    CHILD = "CHILD"
    patient_code = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=160)
    phone = models.CharField(max_length=30, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    dentition_type = models.CharField(max_length=10, choices=[(ADULT, "Adult"), (CHILD, "Child")], default=ADULT)
    medical_history = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.patient_code} - {self.full_name}"


class Tooth(models.Model):
    code = models.CharField(max_length=4)
    dentition_type = models.CharField(max_length=10, choices=Patient._meta.get_field("dentition_type").choices)
    display_order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["dentition_type", "display_order"]
        constraints = [models.UniqueConstraint(fields=["code", "dentition_type"], name="unique_tooth_code_type")]

    def __str__(self):
        return self.code


class ToothCondition(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="tooth_conditions")
    tooth = models.ForeignKey(Tooth, on_delete=models.PROTECT)
    condition = models.CharField(max_length=120)
    note = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["patient", "tooth"], name="unique_patient_tooth")]


class Appointment(models.Model):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, null=True, blank=True, related_name="appointments")
    dentist_name = models.CharField(max_length=160)
    room = models.CharField(max_length=40, default="Room 01")
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(max_length=20, default=SCHEDULED)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(end_at__gt=models.F("start_at")), name="appointment_end_after_start")
        ]


class Service(models.Model):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    duration_minutes = models.PositiveSmallIntegerField(default=30)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TreatmentPlan(models.Model):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    STATUS_CHOICES = [(DRAFT, "Draft"), (ACTIVE, "Active"), (COMPLETED, "Completed"), (CANCELLED, "Cancelled")]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="treatment_plans")
    dentist = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="treatment_plans")
    title = models.CharField(max_length=180)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TreatmentItem(models.Model):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    CANCELLED = "CANCELLED"
    STATUS_CHOICES = [(PLANNED, "Planned"), (IN_PROGRESS, "In progress"), (DONE, "Done"), (CANCELLED, "Cancelled")]
    plan = models.ForeignKey(TreatmentPlan, on_delete=models.CASCADE, related_name="items")
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name="treatment_items")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, null=True, blank=True, related_name="treatment_items")
    procedure_name = models.CharField(max_length=180)
    tooth = models.ForeignKey(Tooth, on_delete=models.PROTECT, null=True, blank=True, related_name="treatment_items")
    cost = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PLANNED)


class Invoice(models.Model):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PARTIAL = "PARTIALLY_PAID"
    PAID = "PAID"
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="invoices")
    invoice_number = models.CharField(max_length=30, unique=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default=DRAFT)
    issued_at = models.DateTimeField(auto_now_add=True)

    @property
    def balance(self):
        return self.total_amount - self.paid_amount


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, null=True, blank=True, related_name="invoice_items")
    description = models.CharField(max_length=180)
    quantity = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.amount = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class Payment(models.Model):
    CASH = "CASH"
    CARD = "CARD"
    BANK_TRANSFER = "BANK_TRANSFER"
    METHOD_CHOICES = [(CASH, "Cash"), (CARD, "Card"), (BANK_TRANSFER, "Bank transfer")]
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default=CASH)
    paid_at = models.DateTimeField(auto_now_add=True)
    received_by = models.ForeignKey(ClinicUser, on_delete=models.PROTECT, null=True, blank=True, related_name="payments_received")
