from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from ckeditor.fields import RichTextField


class CreatedUpdatedAbstractModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class Faq(CreatedUpdatedAbstractModel):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Contact(CreatedUpdatedAbstractModel):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    topic = models.CharField(max_length=255)
    message = models.TextField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.full_name


class AboutUs(CreatedUpdatedAbstractModel):
    information = RichTextField()

    class Meta:
        verbose_name_plural = "About Us"
        verbose_name = "About Us"

    def __str__(self):
        return self.information


class AboutUsImages(CreatedUpdatedAbstractModel):
    image = models.FileField(upload_to="aboutus/media/")

    class Meta:
        verbose_name_plural = "About Us Images"
        verbose_name = "About Us Images"

    def __int__(self):
        return self.image


class ObjectView(CreatedUpdatedAbstractModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "object_id", "user"],
                name="unique_view_per_user",
                condition=models.Q(user__isnull=False),
            ),
        ]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.content_type} #{self.object_id} viewed by {self.user or self.ip_address}"
