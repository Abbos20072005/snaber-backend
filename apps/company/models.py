from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.authentication.models import User
from apps.core.models import CreatedUpdatedAbstractModel


class Region(CreatedUpdatedAbstractModel):
    name = models.CharField(max_length=150)

    def __str__(self) -> str:
        return self.name


class Industry(CreatedUpdatedAbstractModel):
    name = models.CharField(max_length=150)

    def __str__(self) -> str:
        return self.name


class Company(CreatedUpdatedAbstractModel):
    class CompanyStatus(models.TextChoices):
        DRAFT = "draft", _("Draft")
        ACTIVE = "active", _("Active")
        INACTIVE = "inactive", _("Inactive")
        BLOCKED = "blocked", _("Blocked")

    name = models.CharField(max_length=255, db_index=True)

    status = models.CharField(
        max_length=20,
        choices=CompanyStatus.choices,
        default=CompanyStatus.DRAFT,
    )

    description_moderator = models.TextField(
        blank=True, default=""
    )  # moderator nima uchun statusni tanlaganini yozishi uchun description

    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    # social links
    telegram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    whatsapp = models.URLField(blank=True)
    own_site = models.URLField(blank=True)

    logo = models.FileField(upload_to="companies/logos/", blank=True, null=True)
    cover = models.FileField(upload_to="companies/covers/", blank=True, null=True)
    min_answer_time = models.IntegerField(null=True, blank=True)
    max_answer_time = models.IntegerField(null=True, blank=True)
    min_delivery_time = models.IntegerField(null=True, blank=True)
    max_delivery_time = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)

    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name="companies",
        null=True,
        blank=True,
    )
    address = models.CharField(max_length=500, blank=True)
    longitude = models.FloatField(default=69.2385)
    latitude = models.FloatField(default=41.2982)

    industries = models.ManyToManyField(
        Industry,
        related_name="companies",
        blank=True,
    )
    inn = models.CharField(max_length=9, null=True, validators=[RegexValidator(r"^\d{9}$", message="INN must be 9 digets")])

    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["region", "status"]),
        ]

    def __str__(self) -> str:
        return self.name


class CompanyCertificate(CreatedUpdatedAbstractModel):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="certificates",
    )
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="companies/certificates/")
    earned_at = models.DateField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["company", "earned_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} -> {self.company.name}"


class CompanyGallery(CreatedUpdatedAbstractModel):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="gallery",
    )
    image = models.FileField(upload_to="companies/gallery/")
    title = models.CharField(max_length=255, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["company"]),
        ]

    def __str__(self) -> str:
        return f"Gallery #{self.id} -> {self.company.name}"


class CompanyMember(CreatedUpdatedAbstractModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="company_memberships",
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="members",
    )
    is_owner = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "company"],
                name="unique_company_member_user_company",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user.email} -> {self.company.name}"

    def has_permission(self, permission: str) -> bool:
        if permission == "manage_members":
            return self.is_owner
        return True


class Feature(CreatedUpdatedAbstractModel):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="features",
    )
    name = models.CharField(max_length=255)

    class Meta:
        indexes = [
            models.Index(fields=["company"]),
        ]

    def __str__(self):
        return self.name


class ResponseTimeEntry(CreatedUpdatedAbstractModel):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="response_time_entries",
    )
    conversation = models.ForeignKey(
        "chat.Conversation",
        on_delete=models.CASCADE,
        related_name="response_time_entries",
    )
    buyer_message = models.OneToOneField(
        "chat.Message",
        on_delete=models.CASCADE,
        related_name="response_entry",
    )
    responded_at = models.DateTimeField()
    response_time_seconds = models.PositiveIntegerField()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "-created_at"]),
            models.Index(fields=["conversation", "buyer_message"]),
        ]

    def __str__(self):
        return f"{self.company.name} - {self.response_time_seconds}s"
