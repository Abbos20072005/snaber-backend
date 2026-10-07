from django.contrib import admin

from apps.review.models import Comment, CommentImage


class CommentImageInline(admin.TabularInline):
    model = CommentImage
    extra = 0


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "variant_id", "text", "rating", "created_at")
    list_filter = ("created_at", "rating")
    search_fields = ("user__email", "variant__product__name", "text")
    inlines = [CommentImageInline]
