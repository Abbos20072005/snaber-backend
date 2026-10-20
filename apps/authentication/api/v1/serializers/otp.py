from rest_framework import serializers

from apps.authentication.utils import normalize_phone


class PhoneField(serializers.CharField):
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        try:
            return normalize_phone(value)
        except ValueError as err:
            raise serializers.ValidationError(
                "Enter a valid Uzbekistan phone number.", code="invalid_phone"
            ) from err


class OTPSendSerializer(serializers.Serializer):
    phone_number = PhoneField()


class OTPVerifySerializer(serializers.Serializer):
    phone_number = PhoneField()
    otp_code = serializers.RegexField(r"^\d{6}$")
