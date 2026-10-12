from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, MedicalRecordViewSet

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'medical-records', MedicalRecordViewSet, basename='medical-record')

urlpatterns = [
    path('', include(router.urls)),
]