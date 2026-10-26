from django.db import models
from authentication.models import User
from clinic.models import Doctor, Patient, Service
from clinic.models import Tooth

class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'Pending', 'Chờ xác nhận'
        CONFIRMED = 'Confirmed', 'Đã xác nhận'
        COMPLETED = 'Completed', 'Đã hoàn thành'
        CANCELLED = 'Cancelled', 'Đã hủy'

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_appointments')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["status", "appointment_date"],
                name="appt_status_date_idx",
            ),
        ]

    def __str__(self):
        date_str = self.appointment_date.strftime('%d/%m/%Y %H:%M') if self.appointment_date else ''
        return f"Lịch hẹn: {self.patient} - {date_str}"

class MedicalRecord(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='medical_record')
    diagnosis = models.TextField()  # Chẩn đoán
    treatment_plan = models.TextField()  # Hướng điều trị
    prescription = models.TextField(blank=True, null=True)  # Đơn thuốc
    notes = models.TextField(blank=True, null=True)
    teeth = models.ManyToManyField(Tooth, blank=True, related_name="medical_records")
    services = models.ManyToManyField(Service, blank=True, related_name="medical_records")
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Hồ sơ bệnh án cho lịch hẹn #{self.appointment.id}"


class FollowUpReminder(models.Model):
    class Status(models.TextChoices):
        SENDING = "SENDING", "Sending"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"
        UNKNOWN = "UNKNOWN", "Unknown provider result"

    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name="follow_up_reminders",
    )
    scheduled_for = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices)
    provider_reference = models.CharField(max_length=64, blank=True)
    error_message = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["medical_record", "scheduled_for"],
                name="unique_follow_up_reminder_per_date",
            )
        ]