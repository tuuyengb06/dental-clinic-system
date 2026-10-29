from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AppointmentViewSet,
    FollowUpAppointmentViewSet,
    MedicalRecordViewSet,
)

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'medical-records', MedicalRecordViewSet, basename='medical-record')
router.register(
    r'follow-up-appointments',
    FollowUpAppointmentViewSet,
    basename='follow-up-appointment',
)

urlpatterns = [
    path('', include(router.urls)),
]