from rest_framework import viewsets
from rest_framework.permissions import BasePermission

from .models import Appointment, MedicalRecord
from .serializers import AppointmentSerializer, MedicalRecordSerializer


class IsAppointmentStaff(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        clinic_profile = getattr(request.user, "clinic_profile", None)
        return bool(
            request.user.is_superuser
            or (clinic_profile and clinic_profile.role.code in ("ADMIN", "RECEPTIONIST"))
        )


class IsDentistOrAdmin(BasePermission):
    def has_permission(self, request, view):
        clinic_profile = getattr(request.user, "clinic_profile", None)
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_superuser
                or (
                    clinic_profile
                    and clinic_profile.role.code in ("ADMIN", "DENTIST")
                )
            )
        )


class IsScheduleStaff(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        clinic_profile = getattr(request.user, "clinic_profile", None)
        return bool(
            request.user.is_superuser
            or (clinic_profile and clinic_profile.role.code in ("ADMIN", "RECEPTIONIST"))
        )


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAppointmentStaff]

    def get_queryset(self):
        queryset = Appointment.objects.select_related(
            "patient", "doctor__clinic_user__user", "service"
        )
        clinic_profile = getattr(self.request.user, "clinic_profile", None)
        if clinic_profile and clinic_profile.role.code == "DENTIST":
            return queryset.filter(doctor__clinic_user=clinic_profile)
        return queryset


class MedicalRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsDentistOrAdmin]

    def get_queryset(self):
        queryset = MedicalRecord.objects.select_related(
            "appointment__patient", "appointment__doctor__clinic_user__user"
        ).prefetch_related("teeth", "services")
        clinic_profile = getattr(self.request.user, "clinic_profile", None)
        if clinic_profile and clinic_profile.role.code == "DENTIST":
            return queryset.filter(appointment__doctor__clinic_user=clinic_profile)
        return queryset