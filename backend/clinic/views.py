from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Doctor, WorkSchedule, Service
from .serializers import DoctorSerializer, WorkScheduleSerializer, DentalServiceSerializer

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]

class WorkScheduleViewSet(viewsets.ModelViewSet):
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer
    permission_classes = [IsAuthenticated]

class DentalServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()  # Dùng đúng Service.objects.all()
    serializer_class = DentalServiceSerializer
    permission_classes = [IsAuthenticated]