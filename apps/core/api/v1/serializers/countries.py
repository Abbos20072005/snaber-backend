from rest_framework import serializers


class CountrySerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()
