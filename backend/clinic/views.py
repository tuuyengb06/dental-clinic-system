from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from .models import Doctor, Patient, Tooth, WorkSchedule, Service, Invoice
from appointments.views import (
    AppointmentViewSet,
    IsAppointmentStaff,
    IsScheduleStaff,
    MedicalRecordViewSet,
)
from .serializers import (
    DoctorSerializer,
    DentalServiceSerializer,
    InvoiceSerializer,
    PatientSerializer,
    ToothSerializer,
    WorkScheduleSerializer,
)


class IsClinicAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return request.user and request.user.is_authenticated
        clinic_profile = getattr(request.user, "clinic_profile", None)
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_superuser
                or (clinic_profile and clinic_profile.role.code == "ADMIN")
            )
        )


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAppointmentStaff]


class ToothViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tooth.objects.all()
    serializer_class = ToothSerializer
    permission_classes = [IsAuthenticated]


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Doctor.objects.select_related("clinic_user__user", "clinic_user__role").all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]


class WorkScheduleViewSet(viewsets.ModelViewSet):
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer
    permission_classes = [IsScheduleStaff]

class DentalServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = DentalServiceSerializer
    permission_classes = [IsClinicAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        service = self.get_object()
        service.is_active = False
        service.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related("patient").all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return JsonResponse({"status": "ok"})