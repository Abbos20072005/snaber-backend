from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import CreatedUpdatedAbstractModel

from apps.authentication.models import User


class Notification(CreatedUpdatedAbstractModel):
    class NotificationType(models.TextChoices):
        CHAT = "chat", _("Chat")
        ORDER = "order", _("Order")
        PRODUCT = "product", _("Product")
        COMPANY = "company", _("Company")
        OTHER = "other", _("Other")

    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.OTHER,
    )
    is_read = models.BooleanField(default=False)
    redirect_id = models.IntegerField(null=True, blank=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
