from django.urls import path, include
from rest_framework.routers import DefaultRouter
from appointments.views import FollowUpAppointmentViewSet
from .views import (
    AppointmentViewSet,
    DoctorViewSet,
    DentalServiceViewSet,
    HealthView,
    InvoiceViewSet,
    MedicalRecordViewSet,
    PatientViewSet,
    RadiographViewSet,
    ToothViewSet,
    WorkScheduleViewSet,
)

router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'teeth', ToothViewSet)
router.register(r'radiographs', RadiographViewSet, basename='radiograph')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'medical-records', MedicalRecordViewSet, basename='medical-record')
router.register(
    r'follow-up-appointments',
    FollowUpAppointmentViewSet,
    basename='follow-up-appointment',
)
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'doctors', DoctorViewSet)
router.register(r'schedules', WorkScheduleViewSet)
router.register(r'services', DentalServiceViewSet)

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('', include(router.urls)),
]