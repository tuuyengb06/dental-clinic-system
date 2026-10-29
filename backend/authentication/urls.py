from django.urls import path
from .views import (
    CurrentUserView,
    RegisterView,
    VietnameseTokenObtainPairView,
    VietnameseTokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('token/', VietnameseTokenObtainPairView.as_view(), name='token'),
    path('me/', CurrentUserView.as_view(), name='auth_me'),
    path('login/', VietnameseTokenObtainPairView.as_view(), name='token_obtain_pair'),       # Lấy JWT Token (Đăng nhập)
    path('me/', CurrentUserView.as_view(), name='auth_me'),
    path('token/refresh/', VietnameseTokenRefreshView.as_view(), name='token_refresh'), # Làm mới Token
]
