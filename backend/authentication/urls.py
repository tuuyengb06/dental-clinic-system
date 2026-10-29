from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import CurrentUserView, RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('token/', TokenObtainPairView.as_view(), name='token'),
    path('me/', CurrentUserView.as_view(), name='auth_me'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),       # Lấy JWT Token (Đăng nhập)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Làm mới Token
]