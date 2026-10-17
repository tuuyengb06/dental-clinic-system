from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AppointmentViewSet,
    DoctorViewSet,
    DentalServiceViewSet,
    HealthView,
    InvoiceViewSet,
    MedicalRecordViewSet,
    PatientViewSet,
    ToothViewSet,
    WorkScheduleViewSet,
)

router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'teeth', ToothViewSet)
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'medical-records', MedicalRecordViewSet, basename='medical-record')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'doctors', DoctorViewSet)
router.register(r'schedules', WorkScheduleViewSet)
router.register(r'services', DentalServiceViewSet)

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('', include(router.urls)),
]