from rest_framework import serializers
from apps.notification.models import Notification
from apps.authentication.api.v1.serializers.users import UserSerializer


class NotificationsListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = UserSerializer()
    title = serializers.CharField()
    title_uz = serializers.CharField()
    title_ru = serializers.CharField()
    title_en = serializers.CharField()
    message = serializers.CharField()
    message_uz = serializers.CharField()
    message_ru = serializers.CharField()
    message_en = serializers.CharField()
    notification_type = serializers.CharField()
    is_read = serializers.BooleanField()
    redirect_id = serializers.IntegerField(allow_null=True)
    created_at = serializers.DateTimeField()
