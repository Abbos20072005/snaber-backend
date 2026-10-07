from django.urls import include, path

urlpatterns = [
    path(
        "v1/chat/",
        include(("apps.chat.api.v1.urls", "chat"), namespace="chat"),
    ),
]
