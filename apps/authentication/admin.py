from django.contrib import admin

from apps.authentication.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "phone_number", "is_verified", "created_at")
    search_fields = ("full_name", "phone_number", "email")
