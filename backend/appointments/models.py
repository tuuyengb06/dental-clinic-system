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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Hồ sơ bệnh án cho lịch hẹn #{self.appointment.id}"