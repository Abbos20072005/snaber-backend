from django.db import models

from apps.core.models import CreatedUpdatedAbstractModel


class Conversation(CreatedUpdatedAbstractModel):
    class Type(models.TextChoices):
        PRODUCT = "product", "Product"
        ORDER = "order", "Order"

    product_variant = models.ForeignKey(
        "product.Variant",
        on_delete=models.SET_NULL,
        null=True,
        related_name="conversations",
        blank=True,
    )
    order = models.OneToOneField(
        "order.Order",
        on_delete=models.SET_NULL,
        null=True,
        related_name="conversation",
        blank=True,
    )
    buyer = models.ForeignKey(
        "authentication.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="buyer_conversations",
    )
    seller = models.ForeignKey(
        "authentication.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="seller_conversations",
    )
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.PRODUCT)

    def __str__(self):
        return str(self.id)


class Message(CreatedUpdatedAbstractModel):
    conversation = models.ForeignKey(
        "chat.Conversation",
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
        blank=True,
    )
    sender = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="sent_messages",
        null=True,
        blank=True,
    )
    message = models.TextField(blank=True, default="")
    system_message = models.JSONField(null=True, blank=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class File(CreatedUpdatedAbstractModel):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="files",
        null=True,
        blank=True,
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="uploaded_files",
        null=True,
        blank=True,
    )
    sender = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="chat_files",
        null=True,
        blank=True,
    )
    file = models.FileField(upload_to="chat/files/")

    def __str__(self):
        return str(self.id)
