import uuid

from django.contrib.auth.hashers import check_password, identify_hasher, make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField

from apps.authentication.api.v1.services.user_manager import UserManager
from apps.authentication.utils import validate_number
from apps.core.models import CreatedUpdatedAbstractModel


class User(CreatedUpdatedAbstractModel, AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        BUYER = "buyer", _("Client")
        ADMIN = "admin", _("Admin")

    full_name = models.CharField(max_length=255, blank=True)
    image = models.FileField(upload_to="users/images/", null=True, blank=True)
    username = models.CharField(
        max_length=100, unique=True, default=uuid.uuid4, editable=False
    )
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(
        max_length=14, unique=True, null=True, blank=True, validators=[validate_number]
    )
    password = models.CharField(max_length=255, blank=True)
    role = models.CharField(choices=Roles.choices, default=Roles.BUYER)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(
        default=False,
    )
    is_blocked = models.BooleanField(
        default=False,
    )
    block_reason = models.TextField(blank=True, default="")
    country = CountryField(blank=True, null=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.full_name

    def set_password(self, raw_password: str) -> None:
        self.password = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        if self.password:
            try:
                identify_hasher(self.password)
            except Exception:
                self.set_password(self.password)
        super().save(*args, **kwargs)
