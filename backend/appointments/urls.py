from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, MedicalRecordViewSet

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet)
router.register(r'medical-records', MedicalRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]