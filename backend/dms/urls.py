from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),       # POST /api/auth/login/ and /api/auth/register/
    path('api/clinic/', include('clinic.urls')),             # Đường dẫn quản lý danh mục (Doctor, Service, Schedule)
    path('api/', include('appointments.urls')),              # Đường dẫn lịch hẹn & hồ sơ bệnh án
]
