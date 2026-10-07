from rest_framework import serializers


class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.IntegerField()


class OTPResendSerializer(serializers.Serializer):
    email = serializers.EmailField()
