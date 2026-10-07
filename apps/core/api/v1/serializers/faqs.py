from rest_framework import serializers

from apps.core.models import Faq


class FaqCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = [
            "id",
            "name_uz",
            "name_ru",
            "name_en",
            "description_uz",
            "description_ru",
            "description_en",
        ]


class FaqListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    name_uz = serializers.CharField()
    name_ru = serializers.CharField()
    name_en = serializers.CharField()
    description = serializers.CharField()
    description_uz = serializers.CharField()
    description_ru = serializers.CharField()
    description_en = serializers.CharField()
