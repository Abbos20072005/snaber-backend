from django.urls import path

from apps.chat.api.v1.views.conversations import (
    ConversationListCreateView,
    ConversationMarkReadView,
    ConversationMessagesView,
)

urlpatterns = [
    path(
        "conversations/",
        ConversationListCreateView.as_view(),
        name="conversation-list-create",
    ),
    path(
        "conversations/<int:id>/messages/",
        ConversationMessagesView.as_view(),
        name="conversation-messages-list-create",
    ),
    path(
        "conversations/<int:id>/mark-read/",
        ConversationMarkReadView.as_view(),
        name="conversation-mark-read",
    ),
]
