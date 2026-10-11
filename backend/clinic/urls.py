from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorViewSet, WorkScheduleViewSet, DentalServiceViewSet

router = DefaultRouter()
router.register(r'doctors', DoctorViewSet)
router.register(r'schedules', WorkScheduleViewSet)
router.register(r'services', DentalServiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]