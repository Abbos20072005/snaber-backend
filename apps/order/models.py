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
        # Own products of the buyer count after the admin sets their price.
        self.budget = sum(
            item.price * item.quantity for item in self.items.all()
        ) + sum(
            item.price * item.quantity
            for item in self.custom_items.all()
            if item.price is not None
        )
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


class OrderCustomItem(CreatedUpdatedAbstractModel):
    """A product the buyer added to the order by himself, it is not in the catalog."""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="custom_items"
    )
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    # Unit price, the admin sets it after the product is found. Empty until then.
    price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = "Order custom item"
        verbose_name_plural = "Order custom items"

    def __str__(self):
        return f"{self.name} x{self.quantity}"


class ProductRequest(CreatedUpdatedAbstractModel):
    """A list of products the buyer could not find in the catalog."""

    class Status(models.TextChoices):
        NEW = "new", "New"
        IN_PROGRESS = "in_progress", "In progress"
        DONE = "done", "Done"

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_requests",
    )
    comment = models.TextField(blank=True)
    # A photo of the list or the buyer's own Excel file.
    file = models.FileField(upload_to="requests/files/", null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    answer = models.TextField(blank=True)

    class Meta:
        verbose_name = "Product request"
        verbose_name_plural = "Product requests"

    def __str__(self):
        return f"Request {self.id} - {self.buyer}"


class ProductRequestItem(CreatedUpdatedAbstractModel):
    request = models.ForeignKey(
        ProductRequest, on_delete=models.CASCADE, related_name="items"
    )
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Product request item"
        verbose_name_plural = "Product request items"

    def __str__(self):
        return f"{self.name} x{self.quantity}"
