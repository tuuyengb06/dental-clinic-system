from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Appointment, MedicalRecord
from .serializers import AppointmentSerializer, MedicalRecordSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]


class MedicalRecordViewSet(viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated]