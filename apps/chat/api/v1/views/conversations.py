from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.chat.api.v1.serializers.conversations import (
    ConversationCreateSerializer,
    ConversationListSerializer,
    ConversationMessageFileUploadSerializer,
    MessageSerializer,
)
from apps.chat.api.v1.services.conversations import ConversationService


class ConversationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: ConversationListSerializer(many=True)},
        tags=["Chat"],
        operation_description="List conversations for the authenticated user.",
    )
    def get(self, request):
        return ConversationService(request=request).get_conversations()

    @swagger_auto_schema(
        request_body=ConversationCreateSerializer,
        responses={201: ConversationListSerializer},
        tags=["Chat"],
        operation_description="Create a new conversation. "
        "The authenticated user becomes the buyer.",
    )
    def post(self, request):
        return ConversationService(request=request).create_conversation()


class ConversationMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: MessageSerializer(many=True)},
        tags=["Chat"],
        operation_description="List paginated messages for a conversation. "
        "User must be the buyer or seller.",
    )
    def get(self, request, *args, **kwargs):
        return ConversationService(request=request).get_messages(*args, **kwargs)

    @swagger_auto_schema(
        responses={201: ConversationMessageFileUploadSerializer},
        request_body=ConversationMessageFileUploadSerializer,
        tags=["Chat"],
        operation_description="API to upload file in a chat",
    )
    def post(self, request, *args, **kwargs):
        return ConversationService(request=request).upload_file(*args, **kwargs)


class ConversationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: "Marked as read"},
        tags=["Chat"],
        operation_description="Mark all messages as read for the authenticated user.",
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_PATH,
                description="Conversation ID",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return ConversationService(request=request).mark_conversation_as_read(
            *args, **kwargs
        )
