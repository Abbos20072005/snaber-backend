from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.catalog.models import BaseModel


class OrderStatus(models.TextChoices):
    NEW = "new", "Yangi"
    CONFIRMED = "confirmed", "Tasdiqlangan"
    DONE = "done", "Bajarilgan"
    CANCELLED = "cancelled", "Bekor qilingan"


# Menejer qo'ng'iroq qilib holatni oldinga suradi; yakunlangan buyurtma qayta ochilmaydi.
ALLOWED_TRANSITIONS = {
    OrderStatus.NEW: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.DONE, OrderStatus.CANCELLED},
    OrderStatus.DONE: set(),
    OrderStatus.CANCELLED: set(),
}


class Order(BaseModel):
    name = models.CharField("Mijoz ismi", max_length=100)
    phone = models.CharField("Telefon", max_length=20, db_index=True)
    comment = models.TextField("Izoh", blank=True, default="")
    status = models.CharField(
        "Holati", max_length=20, choices=OrderStatus.choices, default=OrderStatus.NEW
    )
    total = models.PositiveBigIntegerField("Jami, so'm", default=0)
    ip_address = models.GenericIPAddressField("IP manzil", null=True, blank=True)

    class Meta:
        ordering = ("-id",)
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        indexes = [models.Index(fields=("status", "-created_at"))]

    def __str__(self):
        return f"№{self.number} — {self.name}"

    @property
    def number(self):
        return self.pk

    def clean(self):
        if self.pk is None:
            return
        previous = Order.objects.filter(pk=self.pk).values_list("status", flat=True).first()
        if (
            previous
            and previous != self.status
            and self.status not in ALLOWED_TRANSITIONS[previous]
        ):
            raise ValidationError(
                {
                    "status": f"«{OrderStatus(previous).label}» holatidan "
                    f"«{OrderStatus(self.status).label}» holatiga o'tkazib bo'lmaydi"
                }
            )


class OrderItem(BaseModel):
    """Order line; name, sku, price and pack are copied at order time."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "catalog.Product",
        verbose_name="Mahsulot",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
    sku = models.CharField("Artikul", max_length=50)
    name = models.CharField("Nomi", max_length=255)
    price = models.PositiveBigIntegerField("Qadoq narxi, so'm")
    pack = models.PositiveIntegerField("Qadoqda, dona")
    qty = models.PositiveIntegerField("Qadoqlar soni", validators=[MinValueValidator(1)])
    amount = models.PositiveBigIntegerField("Summa, so'm")

    class Meta:
        ordering = ("id",)
        verbose_name = "Buyurtma qatori"
        verbose_name_plural = "Buyurtma tarkibi"

    def __str__(self):
        return f"{self.sku} × {self.qty}"
