from django.urls import path

from apps.product.api.v1.views.attributes import (
    AttributeListCreateView,
    AttributeUpdateDeleteView,
    CategoryFilterableAttributesView,
)
from apps.product.api.v1.views.cart import (
    CartAPIView,
    CartCheckoutAPIView,
    CartUpdateDeleteAPIView,
)
from apps.product.api.v1.views.categories import (
    CategoriesPublicListView,
    CategoryBreadcrumbView,
    CategoryChildListUpdateDeleteView,
    CategoryListCreateView,
    CategoryPublicBreadcrumbView,
    CategoryPublicDetailView,
)
from apps.product.api.v1.views.favourite import FavouriteAPIView
from apps.product.api.v1.views.products import (
    GlobalSearchView,
    ProductDetailUpdateDeleteView,
    ProductDetailView,
    ProductImageDeleteView,
    ProductImageView,
    ProductListCreateView,
    ProductTopView,
)
from apps.product.api.v1.views.units import (
    UnitListCreateView,
    UnitUpdateDeleteView,
)
from apps.product.api.v1.views.values import (
    AttributeValueListCreateView,
    AttributeValueUpdateDeleteView,
)

urlpatterns = [
    # categories
    path(
        "public/categories/",
        CategoriesPublicListView.as_view(),
        name="categories-public-list",
    ),
    path(
        "public/categories/<int:id>/",
        CategoryPublicDetailView.as_view(),
        name="category-public-detail",
    ),
    path(
        "category/",
        CategoryListCreateView.as_view(),
        name="category-list-create",
    ),
    path(
        "category/<int:id>/",
        CategoryChildListUpdateDeleteView.as_view(),
        name="category-child-list-update-delete",
    ),
    path(
        "category/<int:id>/breadcrumb/",
        CategoryBreadcrumbView.as_view(),
        name="category-breadcrumb",
    ),
    path(
        "public/categories/<int:id>/breadcrumbs/",
        CategoryPublicBreadcrumbView.as_view(),
        name="public-category-breadcrumb",
    ),
    # products
    path("", ProductListCreateView.as_view(), name="product-list-create"),
    path(
        "<int:id>/",
        ProductDetailUpdateDeleteView.as_view(),
        name="product-detail-update-delete",
    ),
    path("<int:id>/images/", ProductImageView.as_view(), name="product-image-upload"),
    path(
        "<int:id>/images/<int:image_id>/",
        ProductImageDeleteView.as_view(),
        name="product-image-delete",
    ),
    path("public/", ProductTopView.as_view(), name="product-public"),
    path("public/<int:id>/", ProductDetailView.as_view(), name="product-detail"),
    # favourite and cart
    path("favourite/", FavouriteAPIView.as_view(), name="favourite"),
    path("cart/", CartAPIView.as_view(), name="cart"),
    path("cart/checkout/", CartCheckoutAPIView.as_view(), name="cart-checkout"),
    path(
        "cart/<int:pk>/", CartUpdateDeleteAPIView.as_view(), name="cart-delete-update"
    ),
    # attributes
    path("attributes/", AttributeListCreateView.as_view(), name="attributes-list"),
    path(
        "attributes/<int:id>/",
        AttributeUpdateDeleteView.as_view(),
        name="attribute-update-delete",
    ),
    path(
        "public/filter/",
        CategoryFilterableAttributesView.as_view(),
        name="public-filter",
    ),
    # units
    path("units/", UnitListCreateView.as_view(), name="unit-list"),
    path("units/<int:id>/", UnitUpdateDeleteView.as_view(), name="unit-update-delete"),
    # attribute values
    path(
        "attributes/values/",
        AttributeValueListCreateView.as_view(),
        name="attribute-values-list-create",
    ),
    path(
        "attributes/values/<int:id>/",
        AttributeValueUpdateDeleteView.as_view(),
        name="attribute-values-update-delete",
    ),
    # global search
    path("global-search/", GlobalSearchView.as_view(), name="global-search"),
]
