from django.contrib import admin

from apps.notification.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "title",
        "notification_type",
        "is_read",
        "created_at",
    )
    list_filter = (
        "is_read",
        "notification_type",
        "created_at",
    )
    search_fields = ("title", "message")
    ordering = ("-created_at",)
