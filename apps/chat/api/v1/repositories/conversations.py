from django.db.models import Q

from apps.chat.models import Conversation, Message
from apps.core.exceptions import ObjectNotFoundException


class ConversationRepository:
    def get_by_seller(self, user):
        return Conversation.objects.filter(seller=user)

    def get_by_buyer(self, user):
        return Conversation.objects.filter(buyer=user)

    def get_by_admin(self):
        return Conversation.objects.all()

    def get_by_id(self, conversation_id):
        conversation = Conversation.objects.filter(id=conversation_id).first()
        if not conversation:
            raise ObjectNotFoundException(
                message="Conversation not found",
                message_key="conversation_not_found",
            )
        return conversation

    def get_conversation_for_user(self, conversation_id, user):
        conversation = (
            Conversation.objects.filter(
                id=conversation_id,
            )
            .filter(Q(buyer=user) | Q(seller=user))
            .first()
        )

        if not conversation:
            raise ObjectNotFoundException(
                message="Conversation not found",
                message_key="conversation_not_found",
            )
        return conversation

    def get_messages_by_conversation(self, conversation):
        return Message.objects.filter(
            conversation=conversation, system_message__isnull=True
        ).order_by("created_at")
