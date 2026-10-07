import mimetypes

from django.db import transaction
from rest_framework import serializers

from apps.authentication.models import User
from apps.company.api.v1.serializers.certificates import (
    CompanyCertificateListSerializer,
)
from apps.company.api.v1.serializers.galleries import CompanyGalleryListSerializer
from apps.company.models import Company, CompanyMember, Feature
from apps.core.exceptions import ActionNotAllowedException, BaseUnauthorizedException
from apps.product.models import Product


class RegionListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class IndustryListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class CompanyProductBadgeMixin:
    def get_product_badges(self, obj):
        has_ready_products = getattr(obj, "has_ready_products", None)
        has_rfq_products = getattr(obj, "has_rfq_products", None)

        if has_ready_products is None or has_rfq_products is None:
            product_types = set(
                obj.owner_products.filter(is_active=True)
                .values_list("product_type", flat=True)
                .distinct()
            )

            has_ready_products = bool(
                product_types
                & {
                    Product.ProductType.READY,
                    Product.ProductType.BOTH,
                }
            )

            has_rfq_products = bool(
                product_types
                & {
                    Product.ProductType.MADE_TO_ORDER,
                    Product.ProductType.BOTH,
                }
            )

        if has_ready_products and has_rfq_products:
            return "both"
        elif has_ready_products:
            return "ready"
        elif has_rfq_products:
            return "rfq"

        return None


class CompanyListSerializer(CompanyProductBadgeMixin, serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    logo = serializers.FileField()
    region = RegionListSerializer(read_only=True)
    industries = IndustryListSerializer(read_only=True, many=True)
    product_badges = serializers.SerializerMethodField()
    view_count = serializers.IntegerField()
    # Company draft moderation (status + moderator comment) is hidden from the frontend
    # status = serializers.CharField()
    # description_moderator = serializers.CharField()

    contacts = serializers.SerializerMethodField()
    order_counts = serializers.IntegerField(read_only=True)
    member_counts = serializers.IntegerField(read_only=True)
    inn = serializers.CharField(read_only=True)

    def get_contacts(self, obj):
        return {
            "phone": obj.phone,
            "email": obj.email,
            "telegram": obj.telegram,
            "youtube": obj.youtube,
            "instagram": obj.instagram,
            "facebook": obj.facebook,
            "whatsapp": obj.whatsapp,
            "own_site": obj.own_site,
        }


# Company mini-site (statistics) is disabled for the frontend
# class CompanyStatisticsSerializer(serializers.Serializer):
#     companies = serializers.IntegerField()
#     products = serializers.IntegerField()
#     users = serializers.IntegerField()

class FeatureCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = (
            "name_uz",
            "name_ru",
            "name_en",
        )


class FeatureUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name_uz = serializers.CharField()
    name_ru = serializers.CharField()
    name_en = serializers.CharField()


class FeatureListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    name_uz = serializers.CharField()
    name_ru = serializers.CharField()
    name_en = serializers.CharField()


class CompanyDetailListSerializer(CompanyProductBadgeMixin, serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    name_uz = serializers.CharField()
    name_ru = serializers.CharField()
    name_en = serializers.CharField()
    view_count = serializers.IntegerField()
    description = serializers.CharField(read_only=True)
    description_uz = serializers.CharField(read_only=True)
    description_ru = serializers.CharField(read_only=True)
    description_en = serializers.CharField(read_only=True)
    # Company draft moderation (status) is hidden from the frontend
    # status = serializers.CharField()
    logo = serializers.FileField()
    cover = serializers.SerializerMethodField(
        help_text="Cover details including url and type ('image' or 'video')."
    )
    address = serializers.CharField(read_only=True)
    region = RegionListSerializer(read_only=True)
    industries = IndustryListSerializer(read_only=True, many=True)
    product_badges = serializers.SerializerMethodField()

    certificates = CompanyCertificateListSerializer(read_only=True, many=True)
    gallery = CompanyGalleryListSerializer(read_only=True, many=True)
    features = FeatureListSerializer(many=True)
    inn = serializers.CharField(read_only=True)

    info = serializers.SerializerMethodField()

    def get_cover(self, obj) -> dict | None:
        if not obj.cover:
            return None

        request = self.context.get("request")
        url = obj.cover.url
        if request is not None:
            url = request.build_absolute_uri(url)

        mime_type, _ = mimetypes.guess_type(obj.cover.name)
        cover_type = "other"
        if mime_type:
            if mime_type.startswith("image/"):
                cover_type = "image"
            elif mime_type.startswith("video/"):
                cover_type = "video"

        return {"url": url, "type": cover_type}

    def get_info(self, obj):
        return {
            "min_answer_time": obj.min_answer_time,
            "max_answer_time": obj.max_answer_time,
            "min_delivery_time": obj.min_delivery_time,
            "max_delivery_time": obj.max_delivery_time,
            "longitude": obj.longitude,
            "latitude": obj.latitude,
            "phone": obj.phone,
            "email": obj.email,
            "telegram": obj.telegram,
            "youtube": obj.youtube,
            "instagram": obj.instagram,
            "facebook": obj.facebook,
            "whatsapp": obj.whatsapp,
            "own_site": obj.own_site,
        }


class CompanyCreateSerializer(serializers.ModelSerializer):
    features = FeatureCreateSerializer(many=True)

    class Meta:
        model = Company
        fields = (
            "id",
            "name_uz",
            "name_ru",
            "name_en",
            "description_uz",
            "description_ru",
            "description_en",
            # Company draft moderation (status) is hidden from the frontend
            # "status",
            "phone",
            "email",
            "telegram",
            "youtube",
            "instagram",
            "facebook",
            "whatsapp",
            "own_site",
            "logo",
            "cover",
            "min_answer_time",
            "max_answer_time",
            "min_delivery_time",
            "max_delivery_time",
            "region",
            "address",
            "longitude",
            "latitude",
            "industries",
            "features",
            "inn"
        )

    @transaction.atomic
    def create(self, validated_data):
        features_data = validated_data.pop("features", [])
        industries_data = validated_data.pop("industries", [])

        request = self.context.get("request")
        if not request or not request.user:
            raise BaseUnauthorizedException(
                detail="User must be logged in to create company"
            )

        company = Company.objects.create(**validated_data)

        if request.user.role == User.Roles.SELLER:
            if CompanyMember.objects.filter(user=request.user).exists():
                raise ActionNotAllowedException(detail="Company already exists")
            CompanyMember.objects.create(
                company=company, user=request.user, is_owner=True
            )

        if industries_data:
            company.industries.set(industries_data)

        if features_data:
            Feature.objects.bulk_create(
                [Feature(company=company, **item) for item in features_data]
            )
        return company


class CompanyUpdateSerializer(serializers.ModelSerializer):
    features = FeatureUpdateSerializer(many=True)

    class Meta:
        model = Company
        fields = (
            "id",
            "name_uz",
            "name_ru",
            "name_en",
            "description_uz",
            "description_ru",
            "description_en",
            # Company draft moderation (status) is hidden from the frontend
            # "status",
            "phone",
            "email",
            "telegram",
            "youtube",
            "instagram",
            "facebook",
            "whatsapp",
            "own_site",
            "logo",
            "cover",
            "min_answer_time",
            "max_answer_time",
            "min_delivery_time",
            "max_delivery_time",
            "region",
            "address",
            "longitude",
            "latitude",
            "industries",
            "features",
            "inn"
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        features_data = validated_data.pop("features", None)
        industries_data = validated_data.pop("industries", None)

        instance = super().update(instance, validated_data)

        if industries_data:
            instance.industries.set(industries_data)

        if features_data:
            Feature.objects.bulk_update(
                [
                    Feature(
                        id=item["id"],
                        name_uz=item["name_uz"],
                        name_ru=item["name_ru"],
                        name_en=item["name_en"],
                    )
                    for item in features_data
                    if "id" in item
                ],
                fields=["name_uz", "name_ru", "name_en"],
            )
        return instance


# Company draft moderation (status + moderator comment) is disabled for the frontend
# class DraftCompanySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Company
#         fields = ("id", "status", "description_moderator")


class CompanySerializer(CompanyProductBadgeMixin, serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    logo = serializers.FileField(read_only=True)
    region = RegionListSerializer()
    product_badges = serializers.SerializerMethodField()


class CompanyIndustriesSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)

class CompanyRegionSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
