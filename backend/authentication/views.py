from clinic.models import Doctor, Patient
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    AccountUpdateSerializer,
    AdminPasswordResetSerializer,
    CurrentUserSerializer,
    RegisterSerializer,
)


class IsClinicAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        clinic_profile = getattr(request.user, "clinic_profile", None)
        return bool(
            request.user.is_superuser
            or (clinic_profile and clinic_profile.role.code == "ADMIN")
        )


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny] # Cho phép bất kỳ ai cũng có thể gọi API đăng ký


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(CurrentUserSerializer(request.user).data)

    def patch(self, request):
        serializer = AccountUpdateSerializer(
            request.user,
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(CurrentUserSerializer(user).data)


class AdminPasswordResetView(APIView):
    permission_classes = [IsClinicAdmin]

    def post(self, request, account_type, profile_id):
        if account_type == "doctor":
            profile = (
                Doctor.objects.select_related("clinic_user__user", "clinic_user__role")
                .filter(pk=profile_id)
                .first()
            )
            if profile and profile.clinic_user.role.code != "DENTIST":
                raise ValidationError(
                    {"detail": "Hồ sơ này không liên kết với tài khoản bác sĩ."}
                )
            target_user = profile.clinic_user.user if profile else None
        elif account_type == "patient":
            profile = Patient.objects.select_related("user").filter(
                pk=profile_id
            ).first()
            if profile and not profile.user_id:
                raise ValidationError(
                    {"detail": "Hồ sơ bệnh nhân này chưa liên kết tài khoản đăng nhập."}
                )
            target_user = profile.user if profile else None
            if target_user and getattr(target_user, "clinic_profile", None):
                raise ValidationError(
                    {"detail": "Tài khoản liên kết không phải tài khoản bệnh nhân."}
                )
        else:
            raise ValidationError(
                {"account_type": "Chỉ hỗ trợ tài khoản bác sĩ hoặc bệnh nhân."}
            )

        if target_user is None:
            raise ValidationError(
                {"detail": "Không tìm thấy tài khoản cần đặt lại mật khẩu."}
            )

        serializer = AdminPasswordResetSerializer(
            data=request.data,
            context={"user": target_user},
        )
        serializer.is_valid(raise_exception=True)
        target_user.set_password(serializer.validated_data["new_password"])
        target_user.save(update_fields=["password"])
        return Response(
            {
                "detail": (
                    "Đã đặt lại mật khẩu. Hãy chuyển mật khẩu mới cho người dùng "
                    "qua kênh riêng."
                )
            },
            status=status.HTTP_200_OK,
        )