from rest_framework import serializers

from apps.core.models import LegalClientsInfo


class LegalClientsInfoListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    information = serializers.CharField()
    information_uz = serializers.CharField()
    information_ru = serializers.CharField()
    information_en = serializers.CharField()


class LegalClientsInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalClientsInfo
        fields = ["information_uz", "information_ru", "information_en"]
