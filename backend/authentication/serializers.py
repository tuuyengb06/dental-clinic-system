from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'role', 'first_name', 'last_name']

    def create(self, validated_data):
        # Tạo user và mã hóa mật khẩu bằng hàm create_user chuẩn của Django
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'Patient'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class CurrentUserSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["username", "display_name", "role", "phone"]

    def get_display_name(self, user):
        return user.get_full_name() or user.username

    def get_role(self, user):
        clinic_profile = getattr(user, "clinic_profile", None)
        if clinic_profile:
            return clinic_profile.role.code
        if user.is_superuser:
            return "ADMIN"
        return {
            User.Role.DOCTOR: "DENTIST",
            User.Role.RECEPTIONIST: "RECEPTIONIST",
            User.Role.PATIENT: "PATIENT",
        }.get(user.role, "RECEPTIONIST")

    def get_phone(self, user):
        clinic_profile = getattr(user, "clinic_profile", None)
        return clinic_profile.phone if clinic_profile else user.phone