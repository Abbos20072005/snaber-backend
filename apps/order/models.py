from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import CreatedUpdatedAbstractModel
from config import settings


class Order(CreatedUpdatedAbstractModel):
    class OrderType(models.TextChoices):
        READY = "ready", _("Ready")
        RFQ = "rfq", _("RFQ")
        BOTH = "both", _("Both")

    class OrderStatus(models.TextChoices):
        NEGOTIATION = "negotiation", _("Negotiation")
        ACCEPTED = "accepted", _("Accepted")
        REJECTED = "rejected", _("Rejected")

    is_closed = models.BooleanField(default=False)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    company = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        related_name="company_orders",
        null=True,
        blank=True,
    )
    order_type = models.CharField(
        max_length=10, choices=OrderType.choices, default=OrderType.READY
    )
    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.NEGOTIATION
    )
    budget = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    discount = models.IntegerField(default=0)
    discount_budget = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    accepted_by_buyer = models.BooleanField(default=False)
    accepted_by_seller = models.BooleanField(default=False)
    rejected_by_buyer = models.BooleanField(default=False)
    rejected_by_seller = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        total_price = sum(
            (
                    item.price_min
                    or item.price_max
                    or item.product_variant.price_override
                    or item.product_variant.product.price_min
                    or 0
            ) * item.quantity
            for item in self.items.all()
        )
        self.budget = total_price
        if self.discount:
            self.discount_budget = total_price * (100 - self.discount) / 100
        super().save(update_fields=["budget", "discount_budget"])

    def __str__(self):
        return f"Order {self.id} - {self.buyer} -> {self.company}"


class OrderItem(CreatedUpdatedAbstractModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_variant = models.ForeignKey(
        "product.Variant", on_delete=models.CASCADE, related_name="order_items"
    )
    attribute_stock = models.ForeignKey(
        "product.VariantAttributeStock",
        on_delete=models.SET_NULL,
        related_name="order_items",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        "product.Category", on_delete=models.SET_NULL, null=True, blank=True
    )
    description = models.TextField(default="", blank=True)
    quantity = models.PositiveIntegerField()
    price_min = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    price_max = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.product_variant} x{self.quantity}"


class RFQOrderItemAttribute(models.Model):
    order_item = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, related_name="attributes"
    )
    attribute = models.ForeignKey("product.Attribute", on_delete=models.CASCADE)
    value_option = models.ForeignKey(
        "product.AttributeValue", on_delete=models.SET_NULL, null=True, blank=True
    )
    value = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        verbose_name = "RFQ Order Item Attribute"
        verbose_name_plural = "RFQ Order Item Attributes"

    def __str__(self):
        return (
            f"{self.order_item} - {self.attribute}: {self.value_option or self.value}"
        )
