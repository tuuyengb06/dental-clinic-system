from django.contrib.auth.models import User
from django.db import models


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


class Tooth(models.Model):
    code = models.CharField(max_length=4)
    dentition_type = models.CharField(max_length=10, choices=Patient._meta.get_field("dentition_type").choices)
    display_order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["dentition_type", "display_order"]
        constraints = [models.UniqueConstraint(fields=["code", "dentition_type"], name="unique_tooth_code_type")]


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
    dentist_name = models.CharField(max_length=160)
    room = models.CharField(max_length=40, default="Room 01")
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(max_length=20, default=SCHEDULED)
    notes = models.TextField(blank=True)


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
