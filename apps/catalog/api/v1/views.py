from django.db.models import Prefetch
from django.http import Http404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.catalog.api.v1.filters import parse_catalog_query
from apps.catalog.api.v1.serializers import (
    AttributeListSerializer,
    CategoryRetrieveSerializer,
    CategoryTreeSerializer,
    ProductFacetsSerializer,
    ProductListSerializer,
    ProductRetrieveSerializer,
    ProductRowSerializer,
)
from apps.catalog.browse import (
    CategoryPool,
    build_facets,
    build_variants,
    count_by_child,
    first_available,
    group_key_of,
    order_rows,
    related_ids,
)
from apps.catalog.models import (
    Attribute,
    Category,
    CategoryTableColumn,
    Product,
    ProductAttributeValue,
)
from apps.catalog.services import CategoryTree

RELATED_LIMIT = 8
FEATURED_LIMIT = 10
MAX_LIMIT = 50

CATEGORY_PARAMETER = OpenApiParameter(
    "category",
    OpenApiTypes.STR,
    description="Kategoriya yo'li: consumables/fasteners/bolts-screws. Bo'sh — butun katalog.",
)
SEARCH_PARAMETER = OpenApiParameter(
    "q", OpenApiTypes.STR, description="Nomi yoki artikuli bo'yicha qidiruv, so'zlar bo'yicha"
)
ATTRIBUTE_PARAMETER = OpenApiParameter(
    "attr_{key}",
    OpenApiTypes.STR,
    description=(
        "Xususiyat filtri, takrorlash mumkin: attr_thread=M6&attr_thread=M8. "
        "Bitta xususiyat ichida YOKI, xususiyatlar orasida VA."
    ),
)
LIMIT_PARAMETER = OpenApiParameter("limit", OpenApiTypes.INT, description=f"1–{MAX_LIMIT}")


class CatalogPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 500


def load_tree():
    return CategoryTree.load(
        queryset=Category.objects.select_related("table_group_by").prefetch_related(
            Prefetch(
                "table_columns",
                queryset=CategoryTableColumn.objects.select_related("attribute"),
            )
        )
    )


def ordered_attributes():
    return list(Attribute.objects.select_related("requires_attribute"))


def products_by_ids(ids):
    """Products for API output in the order of `ids`."""
    products = (
        Product.objects.filter(pk__in=ids)
        .select_related("category")
        .prefetch_related(
            Prefetch(
                "attribute_values",
                queryset=ProductAttributeValue.objects.select_related("attribute").order_by(
                    "attribute__order", "attribute_id"
                ),
            )
        )
        .in_bulk()
    )
    return [products[pk] for pk in ids if pk in products]


def parse_limit(params, default):
    try:
        return max(1, min(MAX_LIMIT, int(params.get("limit", default))))
    except (TypeError, ValueError):
        return default


class CatalogTreeAPIView(generics.GenericAPIView):
    """Butun kategoriyalar daraxti: menyu, bosh sahifa, footer uchun."""

    queryset = Category.objects.all()
    serializer_class = CategoryTreeSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    @extend_schema(responses={200: CategoryTreeSerializer(many=True)})
    def get(self, request):
        tree = load_tree()
        serializer = self.get_serializer(tree.roots, many=True, context={"tree": tree})
        return Response(serializer.data)


class AttributeListAPIView(generics.ListAPIView):
    """Xususiyatlar: filtr va jadval ustunlari nomlari, filtr chiqish sharti."""

    queryset = Attribute.objects.select_related("requires_attribute")
    serializer_class = AttributeListSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class CategoryRetrieveAPIView(generics.RetrieveAPIView):
    """Kategoriya: yo'li, ichki kategoriyalari, jadval ko'rinishi.

    Oxirgi darajadagi kategoriya sahifasi mahsulot kartochkasiga ochiladi:
    `first_sku` shu mahsulot.
    """

    queryset = Category.objects.all()
    serializer_class = CategoryRetrieveSerializer
    permission_classes = (AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        tree = load_tree()
        category = tree.find(self.kwargs["path"].strip("/").split("/"))
        if category is None:
            raise Http404

        first_sku = None
        if tree.is_leaf(category.pk):
            rows = order_rows(CategoryPool(tree, category).rows, group_key_of(tree, category))
            first = first_available(rows)
            first_sku = first.sku if first else None

        context = {**self.get_serializer_context(), "tree": tree, "first_sku": first_sku}
        return Response(self.get_serializer(category, context=context).data)


@extend_schema(parameters=[CATEGORY_PARAMETER, SEARCH_PARAMETER, ATTRIBUTE_PARAMETER])
class ProductListAPIView(generics.ListAPIView):
    """Filtrlangan mahsulotlar.

    Oxirgi darajadagi kategoriyada jadval tartibida (guruhlash xususiyati,
    uzunlik, nomi), qolgan hollarda katalog tartibida.
    """

    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductRowSerializer
    permission_classes = (AllowAny,)
    pagination_class = CatalogPagination

    def list(self, request, *args, **kwargs):
        tree = load_tree()
        attributes = {attribute.key: attribute for attribute in ordered_attributes()}
        query = parse_catalog_query(request.query_params, tree, attributes)
        pool = CategoryPool(tree, query.category)
        rows = order_rows(pool.matching(query), group_key_of(tree, query.category))

        page = self.paginate_queryset(rows)
        context = {**self.get_serializer_context(), "tree": tree}
        return self.get_paginated_response(
            ProductRowSerializer(page, many=True, context=context).data
        )


class ProductFacetsAPIView(generics.GenericAPIView):
    """Filtrlar paneli, mahsulotlar soni va ichki kategoriya kartochkalari.

    Parametrlar `products/` bilan bir xil. Oxirgi darajadagi kategoriyada
    `first_sku` — filtrlarga mos ochiladigan mahsulot.
    """

    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductFacetsSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    @extend_schema(parameters=[CATEGORY_PARAMETER, SEARCH_PARAMETER, ATTRIBUTE_PARAMETER])
    def get(self, request):
        tree = load_tree()
        attributes = ordered_attributes()
        query = parse_catalog_query(
            request.query_params, tree, {attribute.key: attribute for attribute in attributes}
        )
        pool = CategoryPool(tree, query.category)
        matching = pool.matching(query)

        first_sku = None
        group_key = group_key_of(tree, query.category)
        if query.category is not None and tree.is_leaf(query.category.pk) and matching:
            first_sku = first_available(order_rows(matching, group_key)).sku

        data = {
            "total": len(matching),
            "facets": build_facets(pool, query, attributes),
            "children": [
                {
                    "slug": child["category"].slug,
                    "name": child["category"].name,
                    "icon": child["category"].icon,
                    "description": child["category"].description,
                    "count": child["count"],
                }
                for child in count_by_child(tree, query.category, matching)
            ],
            "first_sku": first_sku,
        }
        return Response(self.get_serializer(data).data)


class ProductRetrieveAPIView(generics.RetrieveAPIView):
    """Mahsulot sahifasi: xususiyatlar, variant chiplari, kategoriya jadvali."""

    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductRetrieveSerializer
    permission_classes = (AllowAny,)
    lookup_field = "sku"

    def retrieve(self, request, *args, **kwargs):
        product = products_by_ids([self.get_object().pk])[0]
        tree = load_tree()
        family = CategoryPool(tree, tree.nodes[product.category_id]).rows
        context = {
            **self.get_serializer_context(),
            "tree": tree,
            "variants": build_variants(product, family, ordered_attributes()),
            "variant_count": len(family),
        }
        return Response(self.get_serializer(product, context=context).data)


class ProductRelatedAPIView(generics.ListAPIView):
    """O'xshash mahsulotlar: shu kategoriyadan, umumiy xususiyatlari ko'pi oldin."""

    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductRowSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    @extend_schema(parameters=[LIMIT_PARAMETER])
    def get(self, request, *args, **kwargs):
        product = generics.get_object_or_404(self.get_queryset(), sku=kwargs["sku"])
        tree = load_tree()
        family = CategoryPool(tree, tree.nodes[product.category_id]).rows
        ids = related_ids(product, family, parse_limit(request.query_params, RELATED_LIMIT))
        rows = {row.id: row for row in family}
        context = {**self.get_serializer_context(), "tree": tree}
        return Response(
            self.get_serializer([rows[pk] for pk in ids], many=True, context=context).data
        )


class ProductFeaturedAPIView(generics.ListAPIView):
    """Bosh sahifadagi «Хиты продаж»: admin panelda «Ommabop» belgilanganlar."""

    queryset = Product.objects.filter(is_active=True, is_featured=True)
    serializer_class = ProductListSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    @extend_schema(parameters=[LIMIT_PARAMETER])
    def get(self, request, *args, **kwargs):
        limit = parse_limit(request.query_params, FEATURED_LIMIT)
        ids = list(self.get_queryset().order_by("id").values_list("id", flat=True)[:limit])
        context = {**self.get_serializer_context(), "tree": load_tree()}
        return Response(self.get_serializer(products_by_ids(ids), many=True, context=context).data)
