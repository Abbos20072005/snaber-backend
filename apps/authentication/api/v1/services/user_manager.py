from django.contrib.auth.models import BaseUserManager, User
from rest_framework_simplejwt.tokens import RefreshToken


class UserManager(BaseUserManager):
    def authenticate(self, email: str, password: str) -> User | None:
        user = self.filter(email=email, is_verified=True).first()
        if user and user.check_password(password):
            return user

        return None

    def create_user(self, username, password=None, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)

    @staticmethod
    def get_tokens_for_user(user: User) -> dict[str, str]:
        refresh = RefreshToken.for_user(user)
        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }
