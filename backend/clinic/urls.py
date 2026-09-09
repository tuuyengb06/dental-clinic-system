from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, HealthViewSet, InvoiceViewSet, PatientViewSet, ToothViewSet

router = DefaultRouter()
router.register("patients", PatientViewSet)
router.register("appointments", AppointmentViewSet)
router.register("teeth", ToothViewSet)
router.register("invoices", InvoiceViewSet)
router.register("health", HealthViewSet, basename="health")
urlpatterns = [path("", include(router.urls))]
