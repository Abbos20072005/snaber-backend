from django.db import models

from apps.core.models import CreatedUpdatedAbstractModel
from config import settings


class Comment(CreatedUpdatedAbstractModel):
    variant = models.ForeignKey(
        "product.Variant",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    text = models.TextField()
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        constraints = [
            models.UniqueConstraint(
                fields=["variant", "user"],
                name="unique_variant_user_comment",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.variant.product.name} ({self.variant.sku_variant})"

    def delete(self, *args, **kwargs):
        for image in self.images.all():
            image.delete()
        super().delete(*args, **kwargs)


class CommentImage(CreatedUpdatedAbstractModel):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.FileField(upload_to="comments/images/")

    class Meta:
        verbose_name = "Comment Image"
        verbose_name_plural = "Comment Images"

    def __str__(self):
        return f"Image for comment {self.comment.id}"

    def delete(self, *args, **kwargs):
        storage = self.image.storage
        path = self.image.name
        super().delete(*args, **kwargs)
        if path:
            try:
                storage.delete(path)
            except NotImplementedError:
                pass
