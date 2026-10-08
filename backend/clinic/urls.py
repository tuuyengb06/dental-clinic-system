from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, CurrentUserView, DoctorDirectoryViewSet, HealthViewSet, InvoiceViewSet, PatientViewSet, ServiceViewSet, ToothViewSet

router = DefaultRouter()
router.register("patients", PatientViewSet)
router.register("appointments", AppointmentViewSet)
router.register("teeth", ToothViewSet)
router.register("invoices", InvoiceViewSet)
router.register("services", ServiceViewSet)
router.register("doctors", DoctorDirectoryViewSet, basename="doctor-directory")
router.register("health", HealthViewSet, basename="health")
urlpatterns = [
    path("auth/me/", CurrentUserView.as_view(), name="current-user"),
    path("", include(router.urls)),
]
