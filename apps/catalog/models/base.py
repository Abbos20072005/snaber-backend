from django.conf import settings
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField("Yaratilgan", auto_now_add=True)
    modified_at = models.DateTimeField("O'zgartirilgan", auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Yaratgan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name="+",
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="O'zgartirgan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name="+",
    )

    class Meta:
        abstract = True
