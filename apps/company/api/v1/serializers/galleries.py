from rest_framework import serializers

from apps.company.models import CompanyGallery


class CompanyGalleryListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    image = serializers.FileField(read_only=True)
    title = serializers.CharField(read_only=True)
    title_uz = serializers.CharField(read_only=True)
    title_ru = serializers.CharField(read_only=True)
    title_en = serializers.CharField(read_only=True)


class CompanyGalleryCreateUpdateSerializer(serializers.ModelSerializer):
    image = serializers.FileField(allow_null=True, required=False)

    class Meta:
        model = CompanyGallery
        fields = (
            "id",
            "company",
            "title_uz",
            "title_ru",
            "title_en",
            "image",
        )
