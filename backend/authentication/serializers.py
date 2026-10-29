from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[(User.Role.PATIENT, 'Bệnh nhân')], default=User.Role.PATIENT)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'role', 'first_name', 'last_name']

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        return User.objects.create_user(password=password, **validated_data)


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