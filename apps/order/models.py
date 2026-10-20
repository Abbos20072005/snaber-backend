from django.db import models

from apps.core.models import CreatedUpdatedAbstractModel
from config import settings


class Order(CreatedUpdatedAbstractModel):
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    budget = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.budget = sum(item.price * item.quantity for item in self.items.all())
        super().save(update_fields=["budget"])

    def __str__(self):
        return f"Order {self.id} - {self.buyer}"


class OrderItem(CreatedUpdatedAbstractModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "product.Product", on_delete=models.CASCADE, related_name="order_items"
    )
    quantity = models.PositiveIntegerField()
    # Unit price at the time of the order, so later price changes don't rewrite history.
    price = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.final_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product} x{self.quantity}"
