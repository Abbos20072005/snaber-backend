from django.db import transaction
from rest_framework import status

from apps.authentication.models import User
from apps.company.models import CompanyMember
from apps.core.exceptions import ObjectNotFoundException, PermissionDeniedException
from apps.core.services import BaseService
from apps.product.api.v1.repositories.constructors import ConstructorRepository
from apps.product.api.v1.repositories.products import ProductRepository
from apps.product.api.v1.repositories.variants import ProductVariantRepository
from apps.product.api.v1.serializers.constructors import (
    ConstructorReviewSerializer,
    ProductConstructorCreateUpdateSerializer,
    ProductConstructorDetailSerializer,
    ProductConstructorListSerializer,
    VariantConstructorCreateUpdateSerializer,
    VariantConstructorListSerializer,
)
from apps.product.api.v1.serializers.products import ProductListSerializer
from apps.product.models import (
    Characteristic,
    Product,
    ProductAttributeValue,
    ProductConstructor,
    Variant,
    VariantAttributeStock,
    VariantMedia,
)


class ConstructorService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = ConstructorRepository()
        self.product_db = ProductRepository()
        self.variant_db = ProductVariantRepository()

    def _get_membership(self, raise_if_missing=True):
        membership = (
            CompanyMember.objects.select_related("company")
            .filter(user=self.request.user)
            .first()
        )
        if not membership and raise_if_missing:
            raise ObjectNotFoundException(message="No company related to this user")
        return membership

    # ── Seller: list / create ────────────────────────────────────────────────

    def list_constructors(self, *args, **kwargs):
        user = self.request.user
        if user.role in (
            User.Roles.ADMIN,
            User.Roles.SUPER_ADMIN,
            User.Roles.MODERATOR,
        ):
            products = self.product_db.get_products()
        else:
            membership = self._get_membership(raise_if_missing=False)
            if not membership:
                return self.get_paginated_response(
                    [], context={"request": self.request}
                )
            products = self.product_db.get_products(company=membership.company)
        return self.get_paginated_response(
            products,
            ProductListSerializer,
            context={"request": self.request},
        )

    def delete_constructor(self, *args, **kwargs):
        user = self.request.user
        constructor = self.db.get_product_constructor(constructor_id=kwargs.get("id"))

        if user.role not in (User.Roles.ADMIN, User.Roles.SUPER_ADMIN):
            membership = self._get_membership()
            if constructor.owner_id != membership.company_id:
                raise PermissionDeniedException()

        self.db.delete_product_constructor(constructor_id=constructor.id)
        return self.get_response_object(status_code=status.HTTP_204_NO_CONTENT)

    def delete_variant_constructor(self, *args, **kwargs):
        user = self.request.user
        variant_constructor = self.variant_db.get_constructor(
            constructor_id=kwargs.get("id")
        )

        if user.role not in (User.Roles.ADMIN, User.Roles.SUPER_ADMIN):
            membership = self._get_membership()
            if (
                variant_constructor.product_constructor.owner_id
                != membership.company_id
            ):
                raise PermissionDeniedException()

        self.variant_db.delete_variant_constructor(
            constructor_id=variant_constructor.id
        )
        return self.get_response_object(status_code=status.HTTP_204_NO_CONTENT)

    def retrieve_constructor(self, *args, **kwargs):
        constructor = self.db.get_product_constructor(constructor_id=kwargs.get("id"))
        return self.get_response_object(
            constructor,
            ProductConstructorDetailSerializer,
            context={"request": self.request},
        )

    def create_constructor(self, *args, **kwargs):
        membership = self._get_membership(raise_if_missing=False)
        serializer = ProductConstructorCreateUpdateSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop("owner", None)
        # Company feature is disabled for the frontend:
        # constructor can be created without a company
        constructor = serializer.save(
            owner=membership.company if membership else None,
            creator=self.request.user,
            status=ProductConstructor.Status.MODERATION,
        )
        return self.get_response_object(
            constructor,
            ProductConstructorListSerializer,
            context={"request": self.request},
            status_code=status.HTTP_201_CREATED,
        )

    def create_variant_constructor(self, *args, **kwargs):
        serializer = VariantConstructorCreateUpdateSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        variant_constructor = serializer.save()
        return self.get_response_object(
            variant_constructor,
            VariantConstructorListSerializer,
            context={"request": self.request},
            status_code=status.HTTP_201_CREATED,
        )

    # ── Seller: update via constructor ───────────────────────────────────────

    def update_product_via_constructor(self, *args, **kwargs):
        constructor = self.db.get_product_constructor(constructor_id=kwargs.get("id"))

        serializer = ProductConstructorCreateUpdateSerializer(
            data=self.request.data,
            instance=constructor,
            partial=True,
            context={"request": self.request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop("owner", None)
        updated = serializer.save(status=ProductConstructor.Status.MODERATION)

        return self.get_response_object(
            updated,
            ProductConstructorListSerializer,
            context={"request": self.request},
        )

    def update_variant_via_constructor(self, *args, **kwargs):
        variant_constructor = self.variant_db.get_constructor(
            constructor_id=kwargs.get("id")
        )

        serializer = VariantConstructorCreateUpdateSerializer(
            data=self.request.data,
            instance=variant_constructor,
            partial=True,
            context={"request": self.request},
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()

        product_constructor = variant_constructor.product_constructor
        product_constructor.status = ProductConstructor.Status.MODERATION
        product_constructor.save(update_fields=["status"])

        return self.get_response_object(
            updated,
            VariantConstructorListSerializer,
            context={"request": self.request},
        )

    # ── Moderator/Admin: review ──────────────────────────────────────────────

    def list_draft_constructors(self, *args, **kwargs):
        user = self.request.user
        if user.role in (User.Roles.ADMIN, User.Roles.SUPER_ADMIN):
            constructors = self.db.get_pending_constructors()
        else:
            membership = (
                CompanyMember.objects.select_related("company")
                .filter(user=user)
                .first()
            )
            if not membership:
                return self.get_paginated_response(
                    [], context={"request": self.request}
                )
            constructors = self.db.get_pending_constructors(membership.company)
        return self.get_paginated_response(
            constructors,
            ProductConstructorListSerializer,
            context={"request": self.request},
        )

    def review_constructor(self, *args, **kwargs):
        constructor = self.db.get_product_constructor(constructor_id=kwargs.get("id"))
        serializer = ConstructorReviewSerializer(
            data=self.request.data,
            instance=constructor,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()

        if updated.status == ProductConstructor.Status.ACCEPTED:
            self._apply_constructor(updated)

        return self.get_response_object(
            updated,
            ProductConstructorListSerializer,
            context={"request": self.request},
        )

    # ── Internal ─────────────────────────────────────────────────────────────

    @transaction.atomic
    def _apply_constructor(self, constructor):
        if constructor.original_product_id:
            product = constructor.original_product
            product.name_uz = constructor.name_uz
            product.name_ru = constructor.name_ru
            product.name_en = constructor.name_en
            product.category = constructor.category
            product.sku = constructor.sku
            product.image = constructor.image
            product.product_type = constructor.product_type
            product.price_type = constructor.price_type
            product.price_min = constructor.price_min
            product.price_max = constructor.price_max
            product.moq = constructor.moq
            product.moq_unit = constructor.moq_unit
            product.lead_time_min = constructor.lead_time_min
            product.lead_time_max = constructor.lead_time_max
            product.save()
        else:
            product = Product.objects.create(
                name_uz=constructor.name_uz,
                name_ru=constructor.name_ru,
                name_en=constructor.name_en,
                creator=constructor.creator,
                owner=constructor.owner,
                category=constructor.category,
                sku=constructor.sku,
                image=constructor.image,
                product_type=constructor.product_type,
                price_type=constructor.price_type,
                price_min=constructor.price_min,
                price_max=constructor.price_max,
                moq=constructor.moq,
                moq_unit=constructor.moq_unit,
                lead_time_min=constructor.lead_time_min,
                lead_time_max=constructor.lead_time_max,
            )
            constructor.original_product = product
            constructor.save(update_fields=["original_product"])

        for vc in constructor.variant_constructors.prefetch_related(
            "variant_media_constructors",
            "attribute_value_constructors",
            "characteristic_constructors",
            "attribute_stock_constructors",
        ).all():
            if vc.original_variant_id:
                variant = vc.original_variant
                variant.description_uz = vc.description_uz
                variant.description_ru = vc.description_ru
                variant.description_en = vc.description_en
                variant.sku_variant = vc.sku_variant
                variant.price_override = vc.price_override
                variant.moq_override = vc.moq_override
                variant.stock_quantity = vc.stock_quantity
                variant.save()
                variant.product_variant_medias.all().delete()
                variant.product_attribute_values.all().delete()
                Characteristic.objects.filter(product_variant=variant).delete()
            else:
                variant = Variant.objects.create(
                    product=product,
                    description_uz=vc.description_uz,
                    description_ru=vc.description_ru,
                    description_en=vc.description_en,
                    sku_variant=vc.sku_variant,
                    price_override=vc.price_override,
                    moq_override=vc.moq_override,
                    stock_quantity=vc.stock_quantity,
                )
                vc.original_variant = variant
                vc.save(update_fields=["original_variant"])

            VariantMedia.objects.bulk_create(
                [
                    VariantMedia(
                        user=m.user,
                        product_variant=variant,
                        file=m.file,
                        product_media_type=m.media_type,
                    )
                    for m in vc.variant_media_constructors.all()
                ]
            )
            ProductAttributeValue.objects.bulk_create(
                [
                    ProductAttributeValue(
                        product=variant,
                        attribute=a.attribute,
                        attribute_value=a.attribute_value,
                    )
                    for a in vc.attribute_value_constructors.all()
                ]
            )
            Characteristic.objects.bulk_create(
                [
                    Characteristic(
                        product_variant=variant,
                        name=c.name,
                        value=c.value,
                    )
                    for c in vc.characteristic_constructors.all()
                ]
            )
            variant.attribute_stocks.all().delete()
            for sc in vc.attribute_stock_constructors.prefetch_related(
                "attribute_values"
            ).all():
                stock = VariantAttributeStock.objects.create(
                    variant=variant,
                    quantity=sc.quantity,
                )
                stock.attribute_values.set(sc.attribute_values.all())
