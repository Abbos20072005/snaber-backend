from rest_framework import serializers

from apps.core.models import Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            "id",
            "full_name",
            "email",
            "topic",
            "message",
        ]
