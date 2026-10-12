from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClinicAppointmentViewSet,
    DoctorViewSet,
    DentalServiceViewSet,
    HealthView,
    InvoiceViewSet,
    PatientViewSet,
    WorkScheduleViewSet,
)

router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'appointments', ClinicAppointmentViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'doctors', DoctorViewSet)
router.register(r'schedules', WorkScheduleViewSet)
router.register(r'services', DentalServiceViewSet)

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('', include(router.urls)),
]