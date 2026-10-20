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
        extra_kwargs = {
            "unit_uz": {"required": True, "allow_blank": False},
            "unit_ru": {"required": False, "allow_blank": True},
            "unit_en": {"required": False, "allow_blank": True},
        }

    def validate(self, attrs):
        # Uzbek is required; Russian and English default to it until translated.
        source = attrs.get("unit_uz")
        if source is None:
            return attrs
        for lang in ("ru", "en"):
            key = f"unit_{lang}"
            current = getattr(self.instance, key, "") if self.instance else ""
            if not attrs.get(key) and not current:
                attrs[key] = source
        return attrs
