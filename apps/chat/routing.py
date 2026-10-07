from django.urls import path

from apps.chat import consumers

websocket_urlpatterns = [
    path("ws/chat/<int:conversation_id>/", consumers.ChatConsumer.as_asgi()),
]
