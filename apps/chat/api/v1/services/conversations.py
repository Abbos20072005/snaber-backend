from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import status

from apps.authentication.models import User
from apps.chat.api.v1.repositories.conversations import ConversationRepository
from apps.chat.api.v1.serializers.conversations import (
    ConversationCreateSerializer,
    ConversationListSerializer,
    ConversationMessageFileUploadSerializer,
    MessageSerializer,
)
from apps.chat.models import Message
from apps.core.services import BaseService


class ConversationService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = ConversationRepository()

    def get_conversations(self):
        user = self.request.user
        if user.role == User.Roles.BUYER:
            conversations = self.db.get_by_buyer(user=user)
        elif user.role == User.Roles.SELLER:
            conversations = self.db.get_by_seller(user=user)
        elif user.role in (User.Roles.ADMIN, User.Roles.SUPER_ADMIN):
            conversations = self.db.get_by_admin()
        else:
            conversations = []
        return self.get_paginated_response(
            conversations, ConversationListSerializer, context={"request": self.request}
        )

    def create_conversation(self):
        serializer = ConversationCreateSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save(buyer=self.request.user)

        return self.get_response_object(
            conversation,
            ConversationListSerializer,
            context={"request": self.request},
            status_code=status.HTTP_201_CREATED,
        )

    def get_messages(self, *args, **kwargs):
        conversation_id = kwargs.get("id")
        user = self.request.user
        if user.role == User.Roles.ADMIN:
            conversation = self.db.get_by_id(conversation_id)
        else:
            conversation = self.db.get_conversation_for_user(conversation_id, user)
        messages = self.db.get_messages_by_conversation(conversation)
        return self.get_paginated_response(
            messages,
            MessageSerializer,
            context={"request": self.request},
        )

    def upload_file(self, *args, **kwargs):
        serializer = ConversationMessageFileUploadSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        conversation_id = kwargs.get("id")
        if user.role == User.Roles.ADMIN:
            conversation = self.db.get_by_id(conversation_id)
        else:
            conversation = self.db.get_conversation_for_user(conversation_id, user)
        message_file = serializer.save(sender=user, conversation=conversation)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"conversation_{conversation.id}",
            {
                "type": "chat_message",
                "id": message_file.id,
                "sender": user.id,
                "message": message_file.message,
                "files": [
                    {"id": f.id, "file": self.request.build_absolute_uri(f.file.url)}
                    for f in message_file.files.all()
                ],
                "created_at": message_file.created_at.isoformat(),
            },
        )

        return self.get_response_object(
            message_file,
            ConversationMessageFileUploadSerializer,
            context={"request": self.request},
            status_code=status.HTTP_201_CREATED,
        )

    def mark_conversation_as_read(self, *args, **kwargs):
        conversation_id = kwargs.get("id")
        user = self.request.user
        if user.role in [User.Roles.SELLER, User.Roles.BUYER]:
            conversation = self.db.get_conversation_for_user(conversation_id, user)
            Message.objects.filter(conversation=conversation, is_read=False).exclude(
                sender=user
            ).update(is_read=True)
            return self.get_response_object(
                {"message": "Marked as read", "result": {}},
                status_code=status.HTTP_200_OK,
            )

        return self.get_response_object(
            {"message": "No messages mark as read", "result": {}},
            status_code=status.HTTP_200_OK,
        )
