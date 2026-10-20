from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.catalog.models.base import BaseModel
from apps.catalog.utils import normalize_search, normalize_value, value_rank


class StockStatus(models.TextChoices):
    IN_STOCK = "in-stock", "Mavjud"
    LOW = "low", "Kam qolgan"
    ON_ORDER = "on-order", "Buyurtma asosida"


class Product(BaseModel):
    sku = models.CharField(
        "Artikul", max_length=50, unique=True, help_text="Sayt manzili: /product/{artikul}"
    )
    name = models.CharField("Nomi", max_length=255)
    category = models.ForeignKey(
        "catalog.Category",
        verbose_name="Kategoriya",
        on_delete=models.PROTECT,
        related_name="products",
    )
    price = models.PositiveBigIntegerField("Narx, so'm", help_text="Bitta qadoq narxi")
    pack = models.PositiveIntegerField(
        "Qadoqda, dona", default=1, validators=[MinValueValidator(1)]
    )
    stock = models.CharField(
        "Ombordagi holati",
        max_length=10,
        choices=StockStatus.choices,
        default=StockStatus.IN_STOCK,
    )
    is_featured = models.BooleanField(
        "Ommabop", default=False, help_text="Bosh sahifadagi «Хиты продаж» qatori"
    )
    is_active = models.BooleanField("Faol", default=True)
    search_text = models.TextField(editable=False, default="")

    class Meta:
        ordering = ("id",)
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        indexes = [models.Index(fields=("category", "is_active"))]

    def __str__(self):
        return f"{self.sku} — {self.name}"

    def save(self, *args, **kwargs):
        self.sku = self.sku.strip()
        self.search_text = normalize_search(f"{self.name} {self.sku}")
        update_fields = kwargs.get("update_fields")
        if update_fields is not None and {"name", "sku"} & set(update_fields):
            kwargs["update_fields"] = {*update_fields, "search_text"}
        super().save(*args, **kwargs)

    def clean(self):
        if self.category_id and self.category.children.exists():
            raise ValidationError(
                {"category": "Mahsulot faqat oxirgi darajadagi kategoriyaga biriktiriladi"}
            )


class ProductAttributeValue(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="attribute_values")
    attribute = models.ForeignKey(
        "catalog.Attribute",
        verbose_name="Xususiyat",
        on_delete=models.PROTECT,
        related_name="values",
    )
    value = models.CharField("Qiymati", max_length=255)
    sort_group = models.PositiveSmallIntegerField(editable=False, default=0)
    sort_number = models.FloatField(editable=False, null=True)

    class Meta:
        ordering = ("attribute__order", "attribute_id")
        verbose_name = "Xususiyat qiymati"
        verbose_name_plural = "Xususiyat qiymatlari"
        constraints = [
            models.UniqueConstraint(
                fields=("product", "attribute"),
                name="unique_product_attribute",
                violation_error_message="Mahsulotda bu xususiyat bor",
            )
        ]
        indexes = [
            models.Index(fields=("attribute", "value")),
            models.Index(fields=("attribute", "sort_group", "sort_number", "value")),
        ]

    def __str__(self):
        return f"{self.attribute.label}: {self.value}"

    def save(self, *args, **kwargs):
        self.value = normalize_value(self.value)
        self.sort_group, self.sort_number = value_rank(self.value)
        super().save(*args, **kwargs)
