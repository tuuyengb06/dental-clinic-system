import uuid

from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from clinic.models import Patient
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    full_name = serializers.CharField(max_length=160, write_only=True)
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True, write_only=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "email", "full_name", "phone", "date_of_birth"]

    @transaction.atomic
    def create(self, validated_data):
        full_name = validated_data.pop("full_name").strip()
        phone = validated_data.pop("phone", "").strip()
        date_of_birth = validated_data.pop("date_of_birth", None)
        name_parts = full_name.split(maxsplit=1)
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            role=User.Role.PATIENT,
            first_name=name_parts[0],
            last_name=name_parts[1] if len(name_parts) > 1 else "",
            phone=phone,
        )
        Patient.objects.create(
            user=user,
            patient_code=f"BN-{uuid.uuid4().hex[:12].upper()}",
            full_name=full_name,
            phone=phone,
            date_of_birth=date_of_birth,
        )
        return user


class CurrentUserSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    patient_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["username", "display_name", "role", "phone", "patient_id"]

    def get_display_name(self, user):
        return user.get_full_name() or user.username

    def get_role(self, user):
        clinic_profile = getattr(user, "clinic_profile", None)
        if clinic_profile:
            return clinic_profile.role.code
        if user.is_superuser:
            return "ADMIN"
        if getattr(user, "patient_profile", None):
            return "PATIENT"
        return "UNASSIGNED"

    def get_phone(self, user):
        clinic_profile = getattr(user, "clinic_profile", None)
        return clinic_profile.phone if clinic_profile else user.phone

    def get_patient_id(self, user):
        patient = getattr(user, "patient_profile", None)
        return patient.id if patient else None


class AccountUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    current_password = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["current_password"]):
            raise serializers.ValidationError(
                {"current_password": "Mật khẩu hiện tại không chính xác."}
            )

        username = attrs["username"].strip()
        if User.objects.exclude(pk=user.pk).filter(username=username).exists():
            raise serializers.ValidationError(
                {"username": "Tên đăng nhập này đã được sử dụng."}
            )
        attrs["username"] = username

        new_password = attrs.get("new_password")
        if new_password:
            validate_password(new_password, user=user)
        return attrs

    def update(self, instance, validated_data):
        instance.username = validated_data["username"]
        update_fields = ["username"]
        new_password = validated_data.get("new_password")
        if new_password:
            instance.set_password(new_password)
            update_fields.append("password")
        instance.save(update_fields=update_fields)
        return instance


class AdminPasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate_new_password(self, value):
        validate_password(value, user=self.context["user"])
        return value