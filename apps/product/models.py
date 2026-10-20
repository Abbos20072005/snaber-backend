from decimal import Decimal

from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import CreatedUpdatedAbstractModel


class Category(CreatedUpdatedAbstractModel):
    image = models.FileField(upload_to="categories/files/", null=True)
    code = models.CharField(max_length=255, unique=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )
    level = models.PositiveSmallIntegerField()
    is_leaf = models.BooleanField(default=False)

    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.code} — {self.name}"

    def get_breadcrumbs(self):
        breadcrumbs = []
        current = self

        while current:
            breadcrumbs.append(current)
            current = current.parent

        return list(reversed(breadcrumbs))


class Unit(CreatedUpdatedAbstractModel):
    unit = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Unit"
        verbose_name_plural = "Units"

    def __str__(self):
        return self.unit


class Product(CreatedUpdatedAbstractModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    category = models.ForeignKey(
        "product.Category",
        on_delete=models.CASCADE,
        related_name="category_products",
    )
    sku = models.CharField(max_length=100, blank=True, default="")
    unit = models.ForeignKey(
        "product.Unit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="unit_products",
    )  # dona / metr / kg / rulon / set / juft ...
    price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount_percent = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(100)]
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=1, default=0.0
    )

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ("-created_at",)

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        if not self.discount_percent:
            return self.price
        return (self.price * (100 - self.discount_percent) / Decimal(100)).quantize(
            Decimal("0.01")
        )


class ProductImage(CreatedUpdatedAbstractModel):
    product = models.ForeignKey(
        "product.Product", on_delete=models.CASCADE, related_name="images"
    )
    file = models.FileField(upload_to="products/files/")
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Product image"
        verbose_name_plural = "Product images"
        ordering = ("position", "id")

    def __str__(self):
        return f"{self.product.name} — {self.file}"


class ProductCharacteristic(CreatedUpdatedAbstractModel):
    product = models.ForeignKey(
        "product.Product", on_delete=models.CASCADE, related_name="characteristics"
    )
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Product characteristic"
        verbose_name_plural = "Product characteristics"
        ordering = ("id",)

    def __str__(self):
        return f"{self.name}: {self.value}"


class Attribute(CreatedUpdatedAbstractModel):
    class Type(models.TextChoices):
        TEXT = "text", _("Text")
        NUMBER = (
            "number",
            _("Number"),
        )
        RANGE = "range", _("Range (min–max)")
        SELECT = "select", _("Select (single)")
        MULTISELECT = "multiselect", _("Multi-select")
        BOOLEAN = (
            "boolean",
            _("Boolean"),
        )

    name = models.CharField(
        max_length=200,
    )
    attribute_type = models.CharField(
        max_length=20, choices=Type.choices, default=Type.TEXT
    )

    category = models.ForeignKey(
        "product.Category",
        related_name="attributes",
        on_delete=models.CASCADE,
        null=True,
    )
    is_filterable = models.BooleanField(
        default=True,
    )

    class Meta:
        verbose_name = "Attribute"
        verbose_name_plural = "Attributes"

    def __str__(self):
        return f"{self.category} - {self.name}"


class AttributeValue(CreatedUpdatedAbstractModel):
    attribute = models.ForeignKey(
        "product.Attribute", on_delete=models.CASCADE, related_name="attribute_values"
    )
    value = models.CharField(max_length=255)
    image = models.FileField(
        upload_to="products/attribute_values/images/", null=True, blank=True
    )

    class Meta:
        verbose_name = "Attribute value"
        verbose_name_plural = "Attribute values"

    def __str__(self):
        return f"{self.attribute} - {self.value}"


class ProductAttributeValue(CreatedUpdatedAbstractModel):
    product = models.ForeignKey(
        "product.Product",
        on_delete=models.CASCADE,
        related_name="product_attribute_values",
    )
    attribute = models.ForeignKey("product.Attribute", on_delete=models.CASCADE)
    attribute_value = models.ForeignKey(
        "product.AttributeValue", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("product", "attribute", "attribute_value")


class Favourite(CreatedUpdatedAbstractModel):
    user = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="favourite_user",
        blank=True,
        null=True,
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="favourite_product",
    )
    session_key = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        if self.user:
            return f"{self.user} - {self.product}"
        return f"Guest({self.session_key}) - {self.product}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                condition=models.Q(user__isnull=False),
                name="unique_user_product",
            ),
            models.UniqueConstraint(
                fields=["session_key", "product"],
                condition=~models.Q(session_key=""),
                name="unique_session_product",
            ),
        ]
        ordering = ("-created_at",)


class Cart(CreatedUpdatedAbstractModel):
    user = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="cart_user",
        blank=True,
        null=True,
    )
    session_key = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        if self.user:
            return f"{self.user}"
        return f"Guest({self.session_key})"


class CartItem(CreatedUpdatedAbstractModel):
    cart = models.ForeignKey("Cart", on_delete=models.CASCADE)
    product = models.ForeignKey(
        "product.Product",
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.cart} - {self.product} - {self.quantity}"
