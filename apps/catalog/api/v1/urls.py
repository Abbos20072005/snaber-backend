from django.urls import path

from apps.catalog.api.v1.views import (
    AttributeListAPIView,
    CatalogTreeAPIView,
    CategoryRetrieveAPIView,
    ProductFacetsAPIView,
    ProductFeaturedAPIView,
    ProductListAPIView,
    ProductRelatedAPIView,
    ProductRetrieveAPIView,
)

urlpatterns = [
    # category
    path("tree/", CatalogTreeAPIView.as_view(), name="catalog-tree"),
    path("categories/<path:path>/", CategoryRetrieveAPIView.as_view(), name="catalog-category-detail"),
    # attribute
    path("attributes/", AttributeListAPIView.as_view(), name="catalog-attribute-list"),
    # product
    path("products/", ProductListAPIView.as_view(), name="catalog-product-list"),
    path("products/featured/", ProductFeaturedAPIView.as_view(), name="catalog-product-featured"),
    path("facets/", ProductFacetsAPIView.as_view(), name="catalog-facets"),
    path("products/<str:sku>/", ProductRetrieveAPIView.as_view(), name="catalog-product-detail"),
    path(
        "products/<str:sku>/related/",
        ProductRelatedAPIView.as_view(),
        name="catalog-product-related",
    ),
]
