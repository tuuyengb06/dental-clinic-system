from rest_framework import generics, permissions
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import CurrentUserSerializer, RegisterSerializer


class VietnameseTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        **TokenObtainPairSerializer.default_error_messages,
        "no_active_account": "Tên đăng nhập hoặc mật khẩu không chính xác, hoặc tài khoản đã bị vô hiệu hóa.",
    }


class VietnameseTokenRefreshSerializer(TokenRefreshSerializer):
    default_error_messages = {
        **TokenRefreshSerializer.default_error_messages,
        "no_active_account": "Tài khoản này không còn hoạt động.",
    }

    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except TokenError as error:
            raise serializers.ValidationError(
                {"refresh": "Mã làm mới phiên đăng nhập không hợp lệ hoặc đã hết hạn."}
            ) from error


class VietnameseTokenObtainPairView(TokenObtainPairView):
    serializer_class = VietnameseTokenObtainPairSerializer


class VietnameseTokenRefreshView(TokenRefreshView):
    serializer_class = VietnameseTokenRefreshSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny] # Cho phép bất kỳ ai cũng có thể gọi API đăng ký


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(CurrentUserSerializer(request.user).data)