from django.contrib.auth.hashers import make_password
from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from apps.core.currency_choices import CurrencyChoices

from apps.authentication.models import User
from apps.core.exceptions import (
    NewPasswordRequiredException,
    OldPasswordRequiredException,
    PasswordIncorrectException,
    PasswordsDontMatchException,
    ValidationError,
)


class UserMeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.CharField()
    phone_number = serializers.CharField()
    role = serializers.ChoiceField(choices=User.Roles.choices)
    image = serializers.FileField()
    country = CountryField()
    currency = serializers.ChoiceField(choices=CurrencyChoices.choices)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = User.objects.authenticate(
            email=attrs.get("email"), password=attrs.get("password")
        )
        if not user:
            raise ValidationError(
                message="Invalid email or password",
                message_key="invalid_email_or_password",
            )
        attrs["user"] = user
        return attrs


class UserRegisterSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        choices=[User.Roles.BUYER, User.Roles.SELLER],
        default=User.Roles.BUYER,
    )

    class Meta:
        model = User
        fields = ("id", "full_name", "email", "password", "role", "country")
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"validators": []},
        }

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "email",
        )


class UserRefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("full_name", "email", "phone_number", "image", "currency", "country")


class UserUpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        user = self.instance

        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        if not old_password:
            raise OldPasswordRequiredException("Old password required")

        if not user.check_password(old_password):
            raise PasswordIncorrectException("Incorrect old password")

        if not new_password:
            raise NewPasswordRequiredException("New password required")

        if new_password != confirm_password:
            raise PasswordsDontMatchException("Passwords do not match")

        return attrs


class UserUpdateEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email")


class UsersSerializers(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    role = serializers.ChoiceField(choices=User.Roles.choices)
    is_verified = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    is_staff = serializers.BooleanField(required=False)
    is_blocked = serializers.BooleanField(required=False)
    block_reason = serializers.CharField(required=False)
    country = CountryField(required=False)
    currency = serializers.ChoiceField(choices=CurrencyChoices.choices, required=False)


class UserUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "image",
            "email",
            "phone_number",
            "role",
            "password",
            "is_verified",
            "is_active",
            "is_staff",
            "is_blocked",
            "block_reason",
            "currency",
            "country",
        )


class ForgetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ForgetPasswordVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.IntegerField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise PasswordsDontMatchException("Passwords do not match")
        return attrs
