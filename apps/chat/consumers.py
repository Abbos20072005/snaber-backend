import json
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.chat.models import Conversation


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"conversation_{self.conversation_id}"

        self.user = await self.get_user_from_token()
        if self.user is None:
            await self.close()
            return

        is_participant = await self.is_conversation_participant()
        if not is_participant:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                **text_data_json,
            },
        )

    async def chat_message(self, event):
        event.pop("type", None)
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_user_from_token(self):
        from rest_framework_simplejwt.tokens import AccessToken

        from apps.authentication.models import User

        query_string = self.scope.get("query_string", b"").decode()
        token_list = parse_qs(query_string).get("token", [])
        if not token_list:
            return None
        try:
            user_id = AccessToken(token_list[0])["user_id"]
            return User.objects.get(id=user_id)
        except Exception:
            return None

    @database_sync_to_async
    def is_conversation_participant(self):
        return (
            Conversation.objects.filter(
                id=self.conversation_id,
                buyer_id=self.user.id,
            ).exists()
            or Conversation.objects.filter(
                id=self.conversation_id,
                seller_id=self.user.id,
            ).exists()
        )
