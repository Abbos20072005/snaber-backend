from rest_framework import serializers

from apps.product.models import Unit


class UnitListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    unit = serializers.CharField()
    unit_uz = serializers.CharField()
    unit_ru = serializers.CharField()
    unit_en = serializers.CharField()



class UnitCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ("id", "unit_uz", "unit_ru", "unit_en")
