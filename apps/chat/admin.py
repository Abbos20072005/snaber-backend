from django.contrib import admin

from apps.chat.models import Conversation, File, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("sender", "message", "system_message", "is_read", "created_at")


class FileInline(admin.TabularInline):
    model = File
    extra = 0
    readonly_fields = ("sender", "file", "created_at")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "type",
        "buyer",
        "seller",
        "product_variant",
        "order",
        "created_at",
    )
    list_filter = ("type",)
    search_fields = ("buyer__email", "seller__email")
    readonly_fields = ("created_at", "updated_at")
    inlines = (MessageInline, FileInline)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "is_read", "created_at")
    list_filter = ("is_read",)
    search_fields = ("sender__email", "message")
    readonly_fields = ("created_at", "updated_at")


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "message", "sender", "file", "created_at")
    search_fields = ("sender__email",)
    readonly_fields = ("created_at", "updated_at")
