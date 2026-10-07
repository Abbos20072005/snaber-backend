from django.contrib import admin

from apps.core.models import Contact, Faq, AboutUs


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ["id", "full_name", "email", "topic", "message"]
    list_filter = ["full_name", "email", "topic", "message"]
    search_fields = ["full_name", "email", "topic", "message"]


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "description"]
    list_filter = ["name"]
    search_fields = ["name"]


@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ["id", "information"]
