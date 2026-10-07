from rest_framework import serializers

from apps.core.models import AboutUs, AboutUsImages


class AboutUsListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    information = serializers.CharField()
    information_uz = serializers.CharField()
    information_ru = serializers.CharField()
    information_en = serializers.CharField()


class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = ["information_uz", "information_ru", "information_en"]


class AboutUsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUsImages
        fields = ["image"]
