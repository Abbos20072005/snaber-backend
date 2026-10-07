from rest_framework import serializers

from apps.chat.models import Conversation, File, Message


class ConversationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ("type", "product_variant", "order")
        extra_kwargs = {
            "product_variant": {"required": False, "allow_null": True},
            "order": {"required": False, "allow_null": True},
        }


class ConversationUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    image = serializers.FileField()
    role = serializers.CharField()


class ConversationListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    buyer = ConversationUserSerializer()
    seller = ConversationUserSerializer()
    product_variant = serializers.IntegerField(
        source="product_variant_id", allow_null=True
    )
    order = serializers.IntegerField(source="order_id", allow_null=True)
    unread_message_count = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def get_unread_message_count(self, obj):
        request = self.context.get("request")
        if (
            request
            and hasattr(request, "user")
            and request.user
            and not request.user.is_anonymous
        ):
            return (
                obj.messages.filter(is_read=False).exclude(sender=request.user).count()
            )
        return obj.messages.filter(is_read=False).count()


class MessageFileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    file = serializers.FileField()


class MessageSerializer(serializers.ModelSerializer):
    files = MessageFileSerializer(many=True)

    class Meta:
        model = Message
        fields = (
            "id",
            "sender",
            "message",
            "files",
            "created_at",
        )


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ("id", "file")
        extra_kwargs = {"id": {"read_only": True}}


class ConversationMessageFileUploadSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, required=False)

    class Meta:
        model = Message
        fields = ("id", "message", "files")
        extra_kwargs = {
            "message": {"required": False, "allow_blank": True, "default": ""},
        }

    def create(self, validated_data):
        files_data = validated_data.pop("files", [])
        message = Message.objects.create(**validated_data)
        for file_data in files_data:
            File.objects.create(
                message=message,
                conversation=message.conversation,
                sender=message.sender,
                **file_data,
            )
        return message
