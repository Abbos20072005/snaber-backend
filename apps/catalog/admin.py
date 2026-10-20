from functools import partial

from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from apps.catalog.models import (
    Attribute,
    Category,
    CategoryTableColumn,
    Product,
    ProductAttributeValue,
)
from apps.catalog.services import CategoryTree


class CategoryChoiceField(forms.ModelChoiceField):
    """Shows the full path: «Расходники › Крепёж › Болты»."""

    def __init__(self, *args, tree, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = tree

    def label_from_instance(self, obj):
        return self.tree.get_label(obj.pk)


def category_choice_kwargs(tree, queryset):
    return {
        "queryset": queryset.annotate(tree_position=tree.position_expression()).order_by(
            "tree_position"
        ),
        "form_class": partial(CategoryChoiceField, tree=tree),
    }


class AuthorMixin:
    """Fills `created_by` / `modified_by` of BaseModel rows edited in the admin."""

    @staticmethod
    def _stamp(obj, user):
        if obj.pk is None:
            obj.created_by = user
        obj.modified_by = user

    def save_model(self, request, obj, form, change):
        self._stamp(obj, request.user)
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for obj in instances:
            self._stamp(obj, request.user)
            obj.save()
        formset.save_m2m()


@admin.register(Attribute)
class AttributeAdmin(AuthorMixin, admin.ModelAdmin):
    list_display = ("label", "key", "order", "requires_attribute", "requires_value")
    list_editable = ("order",)
    search_fields = ("label", "key")
    autocomplete_fields = ("requires_attribute",)
    readonly_fields = ("created_at", "modified_at", "created_by", "modified_by")
    fields = (
        "label",
        "key",
        "order",
        "requires_attribute",
        "requires_value",
        "created_at",
        "modified_at",
        "created_by",
        "modified_by",
    )


class CategoryTableColumnInline(admin.TabularInline):
    model = CategoryTableColumn
    fields = ("attribute", "order")
    autocomplete_fields = ("attribute",)
    extra = 0
    verbose_name_plural = "Jadval ustunlari (faqat oxirgi darajadagi kategoriya uchun)"


@admin.register(Category)
class CategoryAdmin(AuthorMixin, admin.ModelAdmin):
    list_display = ("tree_name", "slug", "icon", "branch_products", "order", "add_child")
    list_display_links = ("tree_name",)
    list_editable = ("order",)
    # Ustun bo'yicha saralash daraxt ko'rinishini buzadi.
    sortable_by = ()
    search_fields = ("name", "slug")
    list_per_page = 300
    autocomplete_fields = ("table_group_by",)
    inlines = (CategoryTableColumnInline,)
    readonly_fields = ("created_at", "modified_at", "created_by", "modified_by")
    fields = (
        "parent",
        "name",
        "slug",
        "icon",
        "description",
        "order",
        "table_group_by",
        "created_at",
        "modified_at",
        "created_by",
        "modified_by",
    )

    def get_queryset(self, request):
        # super() ishlatilmaydi: u tartibni annotatsiyadan oldin qo'llaydi.
        tree = CategoryTree.load(active_products_only=False)
        return Category.objects.select_related("parent").annotate(
            tree_position=tree.position_expression(),
            tree_depth=tree.depth_expression(),
            branch_count=tree.branch_count_expression(),
            direct_products=tree.direct_count_expression(),
        )

    def get_ordering(self, request):
        return ("tree_position",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            tree = CategoryTree.load(active_products_only=False)
            # Mahsulotli kategoriyaga ichki kategoriya qo'shilmaydi.
            kwargs.update(
                category_choice_kwargs(tree, Category.objects.filter(products__isnull=True))
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description="Nomi")
    def tree_name(self, obj):
        return format_html(
            '<span style="padding-left:{}px">{}{}</span>',
            obj.tree_depth * 24,
            "└ " if obj.tree_depth else "",
            obj.name,
        )

    @admin.display(description="Mahsulotlar")
    def branch_products(self, obj):
        return obj.branch_count

    @admin.display(description="")
    def add_child(self, obj):
        if obj.direct_products:
            return "—"
        url = reverse("admin:catalog_category_add")
        return format_html('<a href="{}?parent={}">+ ichki kategoriya</a>', url, obj.pk)


class CategoryTreeListFilter(admin.SimpleListFilter):
    """Category filter that also includes everything below the picked category."""

    title = "Kategoriya"
    parameter_name = "category"

    def lookups(self, request, model_admin):
        tree = CategoryTree.load(active_products_only=False)
        return [(category.pk, f"{'· ' * depth}{category.name}") for category, depth in tree.walk()]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        try:
            category_id = int(self.value())
        except ValueError:
            return queryset.none()
        tree = CategoryTree.load(active_products_only=False)
        return queryset.filter(category_id__in=tree.get_descendant_ids(category_id))


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    fields = ("attribute", "value")
    autocomplete_fields = ("attribute",)
    extra = 1


@admin.register(Product)
class ProductAdmin(AuthorMixin, admin.ModelAdmin):
    list_display = (
        "sku",
        "name",
        "category_path",
        "price",
        "pack",
        "stock",
        "is_featured",
        "is_active",
    )
    list_editable = ("is_featured", "is_active")
    list_filter = ("stock", "is_featured", "is_active", CategoryTreeListFilter)
    search_fields = ("sku", "search_text")
    list_per_page = 50
    inlines = (ProductAttributeValueInline,)
    readonly_fields = ("created_at", "modified_at", "created_by", "modified_by")
    fields = (
        "sku",
        "name",
        "category",
        "price",
        "pack",
        "stock",
        "is_featured",
        "is_active",
        "created_at",
        "modified_at",
        "created_by",
        "modified_by",
    )

    def get_queryset(self, request):
        tree = CategoryTree.load(active_products_only=False)
        leaf_ids = [category_id for category_id in tree.nodes if tree.is_leaf(category_id)]
        return (
            super()
            .get_queryset(request)
            .annotate(category_label=tree.label_expression("category_id", leaf_ids))
        )

    def get_search_results(self, request, queryset, search_term):
        # `search_text` kichik harflarda saqlanadi: kirill harflari uchun so'rov ham
        # kichraytiriladi.
        return super().get_search_results(request, queryset, search_term.lower())

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            tree = CategoryTree.load(active_products_only=False)
            kwargs.update(
                category_choice_kwargs(tree, Category.objects.filter(children__isnull=True))
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description="Kategoriya", ordering="category_label")
    def category_path(self, obj):
        return obj.category_label
