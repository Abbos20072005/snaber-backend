from django.contrib.auth.hashers import make_password
from django.db import transaction
from rest_framework import serializers

from apps.authentication.models import User
from apps.authentication.utils import validate_number
from apps.company.models import CompanyMember
from apps.core.exceptions import UserAlreadyExistsException, ValidationError


class UserMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    phone_number = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)


class CompanyMemberSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user = UserMinimalSerializer(read_only=True)
    company = serializers.IntegerField(source="company_id", read_only=True)
    is_owner = serializers.BooleanField(read_only=True)


class CompanyMemberCreateSerializer(serializers.Serializer):
    full_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    phone_number = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise UserAlreadyExistsException()
        return value

    def validate_phone_number(self, value):
        try:
            validate_number(value)
        except Exception as e:
            raise ValidationError(
                "Please enter a valid phone number (e.g. +998901234567)"
            ) from e
        return value

    @transaction.atomic
    def create(self, validated_data):
        company = self.context["company"]

        full_name = validated_data.pop("full_name")
        email = validated_data.pop("email")
        phone_number = validated_data.pop("phone_number")
        password = validated_data.pop("password")

        user = User.objects.create(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            password=make_password(password),
            role=User.Roles.SELLER,
            is_verified=True,
        )

        member = CompanyMember.objects.create(
            user=user,
            company=company,
            is_owner=False,
        )
        return member
