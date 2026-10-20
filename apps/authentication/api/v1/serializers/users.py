from django_countries.serializer_fields import CountryField
from rest_framework import serializers


from apps.authentication.models import User


class UserMeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.CharField(allow_null=True)
    phone_number = serializers.CharField()
    role = serializers.ChoiceField(choices=User.Roles.choices)
    image = serializers.FileField()
    country = CountryField()


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
        fields = ("full_name", "email", "image", "country")


class UsersSerializers(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.EmailField(allow_null=True)
    phone_number = serializers.CharField()
    role = serializers.ChoiceField(choices=User.Roles.choices)
    is_verified = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    is_staff = serializers.BooleanField(required=False)
    is_blocked = serializers.BooleanField(required=False)
    block_reason = serializers.CharField(required=False)
    country = CountryField(required=False)


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
            "country",
        )
