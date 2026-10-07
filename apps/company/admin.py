from django.contrib import admin

from .models import (
    Company,
    CompanyCertificate,
    CompanyGallery,
    CompanyMember,
    Feature,
    Industry,
    Region,
)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


class CompanyCertificateInline(admin.TabularInline):
    model = CompanyCertificate
    extra = 1


class CompanyGalleryInline(admin.TabularInline):
    model = CompanyGallery
    extra = 1


class CompanyMemberInline(admin.TabularInline):
    model = CompanyMember
    extra = 0


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "region")
    search_fields = ("name", "phone", "email")
    list_filter = ("status", "region")

    inlines = (
        CompanyCertificateInline,
        CompanyGalleryInline,
        CompanyMemberInline,
    )


@admin.register(CompanyCertificate)
class CompanyCertificateAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "company", "earned_at")
    search_fields = ("title", "company__name")


@admin.register(CompanyGallery)
class CompanyGalleryAdmin(admin.ModelAdmin):
    list_display = ("id", "company", "title")
    search_fields = ("title", "company__name")


@admin.register(CompanyMember)
class CompanyMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "company", "is_owner")
    search_fields = ("user__email", "company__name")


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "company")
    search_fields = ("name",)
    list_filter = ("name",)
