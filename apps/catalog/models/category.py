from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.catalog.models.base import BaseModel


class CategoryIcon(models.TextChoices):
    """Icon names the frontend knows (`IconKey` in lib/catalog/types.ts)."""

    FASTENERS = "fasteners", "Mahkamlagichlar"
    SCREWS = "screws", "Vintlar"
    NUTS = "nuts", "Gaykalar"
    WASHERS = "washers", "Shaybalar"
    ELECTRICAL = "electrical", "Elektrotexnika"
    CABLE = "cable", "Kabel"
    LIGHTING = "lighting", "Yoritish"
    BULB = "bulb", "Lampa"
    TOOLS = "tools", "Asboblar"
    WRENCH = "wrench", "Kalit"
    SOCKET = "socket", "Kallak"
    TAPE = "tape", "Lenta"
    PIN = "pin", "Shtift"
    ANCHOR = "anchor", "Anker"
    LINK = "link", "Zanjir"
    PLUG = "plug", "Vilka"
    SWITCH = "switch", "Ulagich"
    DRILL = "drill", "Parma"
    RULER = "ruler", "Chizg'ich"
    GLOVE = "glove", "Qo'lqop"
    HELMET = "helmet", "Kaska"
    PIPE = "pipe", "Quvur"
    VALVE = "valve", "Jo'mrak"
    FLASHLIGHT = "flashlight", "Fonar"
    DISC = "disc", "Disk"
    SCISSORS = "scissors", "Qaychi"
    GLASSES = "glasses", "Ko'zoynak"
    DROPLETS = "droplets", "Suyuqlik"
    PANEL = "panel", "Panel"


class Category(BaseModel):
    parent = models.ForeignKey(
        "self",
        verbose_name="Yuqori kategoriya",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
    )
    slug = models.SlugField(
        "Slug",
        max_length=100,
        help_text=(
            "Sayt manzilidagi qism: /catalog/{yuqori}/{slug}. Bir xil darajada takrorlanmaydi."
        ),
    )
    name = models.CharField("Nomi", max_length=200)
    icon = models.CharField(
        "Ikonka", max_length=20, choices=CategoryIcon.choices, default=CategoryIcon.TOOLS
    )
    description = models.TextField("Tavsif", blank=True, default="")
    order = models.PositiveIntegerField(
        "Tartib", default=0, help_text="Bir xil darajada kichigi oldin chiqadi"
    )
    table_group_by = models.ForeignKey(
        "catalog.Attribute",
        verbose_name="Jadvalni guruhlash",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        help_text="Oxirgi darajadagi kategoriya jadvali shu xususiyat bo'yicha guruhlanadi",
    )

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        # NULL lar teng hisoblanmagani uchun yuqori darajadagilar alohida tekshiriladi.
        constraints = [
            models.UniqueConstraint(
                fields=("parent", "slug"),
                condition=Q(parent__isnull=False),
                name="unique_category_slug_in_parent",
                violation_error_message="Bu darajada shunday slug bor",
            ),
            models.UniqueConstraint(
                fields=("slug",),
                condition=Q(parent__isnull=True),
                name="unique_root_category_slug",
                violation_error_message="Yuqori darajada shunday slug bor",
            ),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        if not self.parent_id:
            return

        if self.pk and self._is_ancestor_of(self.parent_id):
            raise ValidationError(
                {
                    "parent": (
                        "Kategoriyani o'zining ichiga yoki ichki kategoriyasiga ko'chirib bo'lmaydi"
                    )
                }
            )
        # Mahsulot faqat oxirgi darajadagi kategoriyada turadi.
        if self.parent.products.exists():
            raise ValidationError(
                {
                    "parent": (
                        "Bu kategoriyada mahsulotlar bor, unga ichki kategoriya qo'shib bo'lmaydi"
                    )
                }
            )

    def _is_ancestor_of(self, category_id):
        parent_by_id = dict(Category.objects.values_list("id", "parent_id"))
        current = category_id
        while current is not None:
            if current == self.pk:
                return True
            current = parent_by_id.get(current)
        return False


class CategoryTableColumn(BaseModel):
    """Attribute column of a leaf category table, in display order."""

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="table_columns")
    attribute = models.ForeignKey(
        "catalog.Attribute",
        verbose_name="Xususiyat",
        on_delete=models.PROTECT,
        related_name="+",
    )
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Jadval ustuni"
        verbose_name_plural = "Jadval ustunlari"
        constraints = [
            models.UniqueConstraint(
                fields=("category", "attribute"),
                name="unique_category_table_column",
                violation_error_message="Bu ustun jadvalda bor",
            )
        ]

    def __str__(self):
        return f"{self.category}: {self.attribute.label}"
