from rest_framework import serializers

from apps.company.models import CompanyCertificate


class CompanyCertificateListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(read_only=True)
    file = serializers.FileField(read_only=True)
    earned_at = serializers.DateField(read_only=True)


class CompanyCertificateCreateUpdateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(allow_null=True, required=False)

    class Meta:
        model = CompanyCertificate
        fields = (
            "id",
            "company",
            "title",
            "file",
            "earned_at",
        )
