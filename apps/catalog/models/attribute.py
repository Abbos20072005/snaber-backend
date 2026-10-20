from django.core.exceptions import ValidationError
from django.db import models

from apps.catalog.models.base import BaseModel


class Attribute(BaseModel):
    """Product characteristic; filters and table columns are built from it."""

    key = models.SlugField(
        "Kalit",
        max_length=50,
        unique=True,
        help_text="Lotin harflarida, masalan thread. API filtrida attr_{kalit} bo'lib ishlatiladi.",
    )
    label = models.CharField("Nomi", max_length=100)
    order = models.PositiveIntegerField(
        "Tartib", default=0, help_text="Filtrlar panelida kichigi yuqorida"
    )
    requires_attribute = models.ForeignKey(
        "self",
        verbose_name="Shart: xususiyat",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dependents",
        help_text="Filtr faqat shu xususiyatning quyidagi qiymati tanlanganda chiqadi",
    )
    requires_value = models.CharField("Shart: qiymat", max_length=255, blank=True, default="")

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Xususiyat"
        verbose_name_plural = "Xususiyatlar"

    def __str__(self):
        return f"{self.label} ({self.key})"

    def clean(self):
        if self.requires_attribute_id and self.requires_attribute_id == self.pk:
            raise ValidationError({"requires_attribute": "Xususiyat o'ziga bog'liq bo'la olmaydi"})
        if self.requires_attribute_id and not self.requires_value.strip():
            raise ValidationError({"requires_value": "Shart uchun qiymatni yozing"})
        if self.requires_value.strip() and not self.requires_attribute_id:
            raise ValidationError({"requires_attribute": "Shart uchun xususiyatni tanlang"})
