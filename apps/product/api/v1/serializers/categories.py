from rest_framework import serializers

from apps.product.models import Category


class CategorySimpleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    name_uz = serializers.CharField()
    name_ru = serializers.CharField()
    name_en = serializers.CharField()
    code = serializers.CharField()
    level = serializers.IntegerField()
    is_leaf = serializers.BooleanField()
    image = serializers.FileField()
    is_active = serializers.BooleanField()


class CategoryListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    name_uz = serializers.CharField()
    name_ru = serializers.CharField()
    name_en = serializers.CharField()
    code = serializers.CharField()
    parent = serializers.SerializerMethodField()
    level = serializers.IntegerField()
    is_leaf = serializers.BooleanField()
    image = serializers.SerializerMethodField()
    is_active = serializers.BooleanField()

    def get_parent(self, obj):
        request = self.context.get("request")
        if obj.parent is None:
            return None
        return CategorySimpleSerializer(obj.parent, context={"request": request}).data

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and hasattr(obj.image, "url"):
            return (
                request.build_absolute_uri(obj.image.url) if request else obj.image.url
            )
        return None


class CategoriesListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    name_uz = serializers.CharField()
    name_ru = serializers.CharField()
    name_en = serializers.CharField()
    code = serializers.CharField()
    parent = serializers.SerializerMethodField()
    level = serializers.IntegerField()
    is_leaf = serializers.BooleanField()
    image = serializers.FileField()
    is_active = serializers.BooleanField()
    children = CategoryListSerializer(many=True)

    def get_parent(self, obj):
        request = self.context.get("request")
        if obj.parent is None:
            return None
        return CategorySimpleSerializer(obj.parent, context={"request": request}).data


class CategoryTreeSerializer(CategoriesListSerializer):
    # Public catalog tree: groups -> sections -> subcategories in one response.
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        request = self.context.get("request")
        sections = []
        for child in obj.children.all():
            section = CategoryListSerializer(child, context={"request": request}).data
            section["children"] = [
                CategoryListSerializer(c, context={"request": request}).data
                for c in child.children.all()
            ]
            sections.append(section)
        return sections


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name_uz",
            "name_ru",
            "name_en",
            "code",
            "parent",
            "image",
            "is_active",
        )


class CategoryBreadcrumbHelperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")


class CategoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name_uz",
            "name_ru",
            "name_en",
            "code",
            "parent",
            "image",
            "is_active",
        )
