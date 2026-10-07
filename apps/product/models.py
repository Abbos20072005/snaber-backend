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
    class ProductType(models.TextChoices):
        READY = "ready", _("Ready")  # Tayyor mahsulot
        MADE_TO_ORDER = "made_to_order", _("Made to order")  # Ishlab chiqarishga
        BOTH = "both", _("Both")  # Ikkalasi

    class PriceType(models.TextChoices):
        EXACT = "exact", _("Exact")  # Aniq narx
        RANGE = "range", _("Range")  # Narx diapazoni
        ON_REQUEST = "on_request", _("On request")  # Narx so'rov bo'yicha

    name = models.CharField(max_length=255)
    creator = models.ForeignKey(
        "authentication.User",
        on_delete=models.SET_NULL,
        related_name="created_products",
        null=True,
        blank=True,
    )
    owner = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        related_name="owner_products",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        "product.Category",
        on_delete=models.CASCADE,
        related_name="category_products",
        null=True,
    )
    sku = models.CharField(max_length=255)
    image = models.FileField(upload_to="products/files/", null=True)
    product_type = models.CharField(
        max_length=20,
        choices=ProductType.choices,
        default=ProductType.READY,
    )
    price_type = models.CharField(
        max_length=20,
        choices=PriceType.choices,
        default=PriceType.ON_REQUEST,
    )
    price_min = models.DecimalField(
        max_digits=55, decimal_places=2, blank=True, default=0
    )
    price_max = models.DecimalField(
        max_digits=55, decimal_places=2, blank=True, default=0
    )
    is_active = models.BooleanField(default=True)
    moq = models.PositiveIntegerField()
    moq_unit = models.ForeignKey(
        "product.Unit",
        on_delete=models.SET_NULL,
        null=True,
        related_name="moq_unit_products",
    )  # dona / metr / kg / rulon / set / juft ...
    lead_time_min = models.PositiveSmallIntegerField(
        blank=True, default=0
    )  # Ishlab chiqarish muddati min (kun)
    lead_time_max = models.PositiveSmallIntegerField(
        blank=True, default=0
    )  # Ishlab chiqarish muddati max (kun)
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=1, default=0.0
    )
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name


class VariantMedia(CreatedUpdatedAbstractModel):
    class MediaType(models.TextChoices):
        PHOTO = "photo", _("Photo")
        VIDEO = "video", _("Video")

    user = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="user_product_variant_medias",
    )
    product_variant = models.ForeignKey(
        "product.Variant",
        on_delete=models.CASCADE,
        related_name="product_variant_medias",
    )
    file = models.FileField(upload_to="products/files/")
    product_media_type = models.CharField(
        max_length=10, choices=MediaType.choices, default=MediaType.PHOTO
    )

    class Meta:
        verbose_name = "Product variant media"
        verbose_name_plural = "Product variant medias"

    def __str__(self):
        return f"{self.user} - {self.product_variant.product.name} - {self.file}"


class Variant(CreatedUpdatedAbstractModel):
    product = models.ForeignKey(
        "product.Product", on_delete=models.CASCADE, related_name="product_variants"
    )
    description = models.TextField(blank=True, default="")
    sku_variant = models.CharField(
        max_length=150,
        blank=True,
    )
    price_override = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
    )
    moq_override = models.PositiveIntegerField(blank=True, default=0)
    stock_quantity = models.PositiveIntegerField(blank=True, default=0)

    is_active = models.BooleanField(default=True)
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=1, default=0.0
    )

    class Meta:
        verbose_name = "Product variant"
        verbose_name_plural = "Product variants"

    def __str__(self):
        return f"{self.product.name}"


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


class Characteristic(CreatedUpdatedAbstractModel):
    product_variant = models.ForeignKey("product.Variant", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ProductAttributeValue(CreatedUpdatedAbstractModel):
    product = models.ForeignKey(
        "product.Variant",
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


class ProductConstructor(CreatedUpdatedAbstractModel):
    class Status(models.TextChoices):
        MODERATION = "moderation", _("Moderation")
        REVIEWING = "reviewing", _("Reviewing")
        RETURNED_FOR_CORRECTION = (
            "returned_for_correction",
            _("Returned for correction"),
        )
        ACCEPTED = "accepted", _("Accepted")

    name = models.CharField(max_length=255)
    creator = models.ForeignKey(
        "authentication.User",
        on_delete=models.SET_NULL,
        related_name="created_product_constructors",
        null=True,
        blank=True,
    )
    owner = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        related_name="owner_product_constructors",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        "product.Category",
        on_delete=models.CASCADE,
        related_name="category_product_constructors",
        null=True,
    )
    sku = models.CharField(max_length=255)
    image = models.FileField(
        upload_to="product_constructors/files/", null=True, blank=True
    )
    product_type = models.CharField(
        max_length=20,
        choices=Product.ProductType.choices,
        default=Product.ProductType.READY,
    )
    price_type = models.CharField(
        max_length=20,
        choices=Product.PriceType.choices,
        default=Product.PriceType.ON_REQUEST,
    )
    price_min = models.DecimalField(
        max_digits=55, decimal_places=2, blank=True, default=0
    )
    price_max = models.DecimalField(
        max_digits=55, decimal_places=2, blank=True, default=0
    )
    is_active = models.BooleanField(default=True)
    moq = models.PositiveIntegerField()
    moq_unit = models.ForeignKey(
        "product.Unit",
        on_delete=models.SET_NULL,
        null=True,
        related_name="moq_unit_product_constructors",
    )
    lead_time_min = models.PositiveSmallIntegerField(blank=True, default=0)
    lead_time_max = models.PositiveSmallIntegerField(blank=True, default=0)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.MODERATION,
    )
    moderator_comment = models.TextField(blank=True, default="")
    original_product = models.OneToOneField(
        "product.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product_constructor",
    )

    class Meta:
        verbose_name = "Product Constructor"
        verbose_name_plural = "Product Constructors"

    def __str__(self):
        return f"{self.name} ({self.status})"


class VariantConstructor(CreatedUpdatedAbstractModel):
    product_constructor = models.ForeignKey(
        "product.ProductConstructor",
        on_delete=models.CASCADE,
        related_name="variant_constructors",
    )
    description = models.TextField(blank=True, default="")
    sku_variant = models.CharField(max_length=150, blank=True)
    price_override = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    moq_override = models.PositiveIntegerField(blank=True, default=0)
    stock_quantity = models.PositiveIntegerField(blank=True, default=0)
    is_active = models.BooleanField(default=True)
    original_variant = models.ForeignKey(
        "product.Variant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="variant_constructors",
    )

    class Meta:
        verbose_name = "Variant Constructor"
        verbose_name_plural = "Variant Constructors"

    def __str__(self):
        return f"{self.product_constructor.name} — variant"


class CharacteristicConstructor(CreatedUpdatedAbstractModel):
    variant_constructor = models.ForeignKey(
        "product.VariantConstructor",
        on_delete=models.CASCADE,
        related_name="characteristic_constructors",
    )
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Characteristic Constructor"
        verbose_name_plural = "Characteristic Constructors"

    def __str__(self):
        return self.name


class VariantMediaConstructor(CreatedUpdatedAbstractModel):
    class MediaType(models.TextChoices):
        PHOTO = "photo", _("Photo")
        VIDEO = "video", _("Video")

    user = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="user_variant_media_constructors",
    )
    variant_constructor = models.ForeignKey(
        "product.VariantConstructor",
        on_delete=models.CASCADE,
        related_name="variant_media_constructors",
    )
    file = models.FileField(upload_to="product_constructors/media/")
    media_type = models.CharField(
        max_length=10,
        choices=MediaType.choices,
        default=MediaType.PHOTO,
    )

    class Meta:
        verbose_name = "Variant Media Constructor"
        verbose_name_plural = "Variant Media Constructors"

    def __str__(self):
        return f"{self.variant_constructor} - {self.file}"


class ProductAttributeValueConstructor(CreatedUpdatedAbstractModel):
    variant_constructor = models.ForeignKey(
        "product.VariantConstructor",
        on_delete=models.CASCADE,
        related_name="attribute_value_constructors",
    )
    attribute = models.ForeignKey("product.Attribute", on_delete=models.CASCADE)
    attribute_value = models.ForeignKey(
        "product.AttributeValue", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("variant_constructor", "attribute", "attribute_value")
        verbose_name = "Product Attribute Value Constructor"
        verbose_name_plural = "Product Attribute Value Constructors"


class VariantAttributeStock(CreatedUpdatedAbstractModel):
    variant = models.ForeignKey(
        "product.Variant",
        on_delete=models.CASCADE,
        related_name="attribute_stocks",
    )
    attribute_values = models.ManyToManyField(
        "product.AttributeValue",
        related_name="variant_attribute_stocks",
    )
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Variant Attribute Stock"
        verbose_name_plural = "Variant Attribute Stocks"

    def __str__(self):
        values = ", ".join(str(v) for v in self.attribute_values.all())
        return f"{self.variant} — [{values}] — {self.quantity}"


class VariantAttributeStockConstructor(CreatedUpdatedAbstractModel):
    variant_constructor = models.ForeignKey(
        "product.VariantConstructor",
        on_delete=models.CASCADE,
        related_name="attribute_stock_constructors",
    )
    attribute_values = models.ManyToManyField(
        "product.AttributeValue",
        related_name="variant_attribute_stock_constructors",
    )
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Variant Attribute Stock Constructor"
        verbose_name_plural = "Variant Attribute Stock Constructors"

    def __str__(self):
        values = ", ".join(str(v) for v in self.attribute_values.all())
        return f"{self.variant_constructor} — [{values}] — {self.quantity}"


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
        "product.Variant",
        on_delete=models.CASCADE,
        related_name="cart_product",
        blank=True,
        null=True,
    )
    attribute_stock = models.ForeignKey(
        "product.VariantAttributeStock",
        on_delete=models.SET_NULL,
        related_name="cart_items",
        null=True,
        blank=True,
    )
    attributes = models.JSONField(default=list, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    company = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart_items",
    )

    def __str__(self):
        return f"{self.cart} - {self.product} - {self.quantity}"
