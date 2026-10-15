from django.contrib import admin
from django.urls import path, include
from appointments.views import AppointmentViewSet

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'api/v1/appointments/',
        AppointmentViewSet.as_view({'get': 'list', 'post': 'create_booking'}),
        name='v1-appointment-list',
    ),
    path(
        'api/v1/appointments/<int:pk>/',
        AppointmentViewSet.as_view({'get': 'retrieve'}),
        name='v1-appointment-detail',
    ),
    path(
        'api/v1/appointments/<int:pk>/cancel/',
        AppointmentViewSet.as_view({'post': 'cancel_booking'}),
        name='v1-appointment-cancel',
    ),
    path(
        'api/v1/appointments/<int:pk>/medical-record/',
        AppointmentViewSet.as_view({
            'get': 'medical_record',
            'post': 'create_medical_record',
            'patch': 'update_medical_record',
            'put': 'update_medical_record',
        }),
        name='v1-appointment-medical-record',
    ),
    path('api/auth/', include('authentication.urls')),       # POST /api/auth/login/ and /api/auth/register/
    path('api/clinic/', include('clinic.urls')),             # Đường dẫn quản lý danh mục (Doctor, Service, Schedule)
    path('api/', include('appointments.urls')),              # Đường dẫn lịch hẹn & hồ sơ bệnh án
]
