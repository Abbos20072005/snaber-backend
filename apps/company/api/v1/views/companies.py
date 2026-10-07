from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.company.api.v1.serializers.companies import (
    CompanyCreateSerializer,
    CompanyDetailListSerializer,
    # Company list (Список компаний) is disabled for the frontend
    # CompanyListSerializer,
    # Company mini-site (statistics) is disabled for the frontend
    # CompanyStatisticsSerializer,
    CompanyUpdateSerializer,
    # Company draft moderation (status + moderator comment) is disabled for the frontend
    # DraftCompanySerializer,
    RegionListSerializer, CompanyIndustriesSerializer, CompanyRegionSerializer,
)
from apps.company.api.v1.services.companies import (
    CompanyService,
)
from apps.core.permissions import (
    IsAdminOrSuperAdmin,
    # Company draft moderation (disabled for the frontend)
    # IsModeratorOrAdmin,
    IsSeller,
    # IsSuperAdmin,
)
# from apps.product.api.v1.serializers.products import ProductListSerializer


class CompanyCreateListView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), (IsSeller | IsAdminOrSuperAdmin)()]
        return [AllowAny()]

    # Company list (Список компаний) is disabled for the frontend
    # @swagger_auto_schema(
    #     responses={200: CompanyListSerializer},
    #     tags=["Company"],
    #     operation_description="Company List",
    # )
    # def get(self, request, *args, **kwargs):
    #     return CompanyService(request=request).get_companies(*args, **kwargs)

    @swagger_auto_schema(
        responses={200: CompanyDetailListSerializer},
        request_body=CompanyCreateSerializer,
        tags=["Company"],
        operation_description="Company create",
    )
    def post(self, request, *args, **kwargs):
        return CompanyService(request=request).create_company(*args, **kwargs)


# Company mini-site (statistics) is disabled for the frontend
# class CompanyStatisticsView(APIView):
#     permission_classes = [AllowAny]
#
#     @swagger_auto_schema(
#         responses={200: CompanyStatisticsSerializer},
#         tags=["Company"],
#         operation_description="Company Statistics",
#     )
#     def get(self, request, *args, **kwargs):
#         return CompanyService(request=request).get_company_statistics(*args, **kwargs)


class CompanyDetailUpdateDeleteView(APIView):
    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [IsAuthenticated(), (IsSeller | IsAdminOrSuperAdmin)()]
        return [AllowAny()]

    @swagger_auto_schema(
        responses={200: CompanyDetailListSerializer},
        tags=["Company"],
        operation_description="Company Detail ",
    )
    def get(self, request, *args, **kwargs):
        return CompanyService(request=request).get_company(*args, **kwargs)

    @swagger_auto_schema(
        tags=["Company"],
        operation_description="Company Delete ",
    )
    def delete(self, request, *args, **kwargs):
        return CompanyService(request=request).delete_company(*args, **kwargs)

    @swagger_auto_schema(
        responses={200: CompanyDetailListSerializer},
        request_body=CompanyUpdateSerializer,
        tags=["Company"],
        operation_description="Company  Update",
    )
    def patch(self, request, *args, **kwargs):
        return CompanyService(request=request).update_company(*args, **kwargs)


# Company mini-site (company products page) is disabled for the frontend
# class CompanyProductView(APIView):
#     permission_classes = [AllowAny]
#
#     @swagger_auto_schema(
#         responses={200: ProductListSerializer},
#         tags=["Company"],
#         operation_description="Company Product",
#         manual_parameters=[
#             openapi.Parameter(
#                 name="category",
#                 in_=openapi.IN_QUERY,
#                 type=openapi.TYPE_INTEGER,
#                 description="Filter by category ID",
#             ),
#             openapi.Parameter(
#                 name="product_type",
#                 in_=openapi.IN_QUERY,
#                 type=openapi.TYPE_STRING,
#                 description="Filter by product type: ready, made_to_order, both",
#             ),
#             openapi.Parameter(
#                 name="price_type",
#                 in_=openapi.IN_QUERY,
#                 type=openapi.TYPE_STRING,
#                 description="Filter by price type: exact, range, on_request",
#             ),
#             openapi.Parameter(
#                 name="price_min",
#                 in_=openapi.IN_QUERY,
#                 type=openapi.TYPE_NUMBER,
#                 description="Filter by minimum price",
#             ),
#             openapi.Parameter(
#                 name="price_max",
#                 in_=openapi.IN_QUERY,
#                 type=openapi.TYPE_NUMBER,
#                 description="Filter by maximum price",
#             ),
#             openapi.Parameter(
#                 name="search",
#                 in_=openapi.IN_QUERY,
#                 type=openapi.TYPE_STRING,
#                 description="Search by product name or SKU",
#             ),
#         ],
#     )
#     def get(self, request, *args, **kwargs):
#         return CompanyService(request=request).get_company_products(*args, **kwargs)


class SellerCompanyView(APIView):
    permission_classes = [IsAuthenticated, IsSeller]

    @swagger_auto_schema(
        responses={200: CompanyDetailListSerializer},
        tags=["Company"],
        operation_description="Companies for Seller ",
    )
    def get(self, request, *args, **kwargs):
        return CompanyService(request=request).get_seller_company(*args, **kwargs)


class RegionListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: RegionListSerializer},
        tags=["Region"],
        operation_description="Region List",
    )
    def get(self, request, *args, **kwargs):
        return CompanyService(request=request).get_regions(*args, **kwargs)


# Company draft moderation (status + moderator comment) is disabled for the frontend
# class DraftCompaniesView(APIView):
#     permission_classes = [IsAuthenticated, IsModeratorOrAdmin | IsSuperAdmin]
#
#     @swagger_auto_schema(
#         responses={200: CompanyListSerializer},
#         tags=["Company"],
#         manual_parameters=[
#             openapi.Parameter(
#                 name="search",
#                 in_=openapi.IN_QUERY,
#                 type=openapi.TYPE_STRING,
#                 description="Company Search by name",
#             ),
#             openapi.Parameter(
#                 name="sort",
#                 in_=openapi.IN_QUERY,
#                 type=openapi.TYPE_STRING,
#                 description="Company sort: new, old, most_products, most_ordered",
#             ),
#             openapi.Parameter(
#                 name="status",
#                 in_=openapi.IN_QUERY,
#                 description="Filter products by status : "
#                 "draft, active, inactive, blocked",
#                 type=openapi.TYPE_STRING,
#             ),
#         ],
#         operation_description="API to get Draft Companies",
#     )
#     def get(self, request, *args, **kwargs):
#         return CompanyService(request=request).get_draft_companies(*args, **kwargs)
#
#
# class DraftCompanyDetailView(APIView):
#     permission_classes = [IsAuthenticated, IsModeratorOrAdmin | IsSuperAdmin]
#
#     @swagger_auto_schema(
#         request_body=DraftCompanySerializer,
#         responses={200: CompanyDetailListSerializer},
#         tags=["Company"],
#         operation_description="API to patch Draft Company",
#     )
#     def patch(self, request, *args, **kwargs):
#         return CompanyService(request=request).update_draft_company(*args, **kwargs)
#
#
# class PublicCompanyDetailView(APIView):
#     permission_classes = [AllowAny]
#
#     @swagger_auto_schema(
#         responses={200: CompanyDetailListSerializer},
#         tags=["Company"],
#         operation_description="Company Detail ",
#     )
#     def get(self, request, *args, **kwargs):
#         return CompanyService(request=request).get_public_company(*args, **kwargs)
#
#
# class PublicCompanyListView(APIView):
#     permission_classes = [AllowAny]
#
#     @swagger_auto_schema(
#         responses={200: CompanyListSerializer},
#         tags=["Company"],
#         manual_parameters=[
#             openapi.Parameter(
#                 name="search",
#                 in_=openapi.IN_QUERY,
#                 type=openapi.TYPE_STRING,
#                 description="Company Search by name",
#             ),
#             openapi.Parameter(
#                 name="sort",
#                 in_=openapi.IN_QUERY,
#                 type=openapi.TYPE_STRING,
#                 description="Company sort: new, old, most_products, most_ordered",
#             ),
#             openapi.Parameter(
#                 name="is_popular",
#                 in_=openapi.IN_QUERY,
#                 description="Filter products by is_popular",
#                 type=openapi.TYPE_BOOLEAN,
#             ),
#             openapi.Parameter(
#                 name="region",
#                 in_=openapi.IN_QUERY,
#                 type=openapi.TYPE_INTEGER,
#                 description="Filter by region",
#             ),
#             openapi.Parameter(
#                 name="industry",
#                 in_=openapi.IN_QUERY,
#                 description="Filter by industries",
#                 type=openapi.TYPE_ARRAY,
#                 items=openapi.Items(type=openapi.TYPE_INTEGER),
#             ),
#             openapi.Parameter(
#                 name="product_type",
#                 in_=openapi.IN_QUERY,
#                 type=openapi.TYPE_STRING,
#                 description="Filter by product_type",
#             )
#         ],
#         operation_description="Company List",
#     )
#     def get(self, request, *args, **kwargs):
#         return CompanyService(request=request).get_public_companies(*args, **kwargs)
#
#
# class PublicCompanyExcelView(APIView):
#     permission_classes = [AllowAny]
#
#     @swagger_auto_schema(
#         tags=["Company"],
#         manual_parameters=[
#             openapi.Parameter(
#                 name="search",
#                 in_=openapi.IN_QUERY,
#                 type=openapi.TYPE_STRING,
#                 description="Company Search by name",
#             ),
#             openapi.Parameter(
#                 name="sort",
#                 in_=openapi.IN_QUERY,
#                 type=openapi.TYPE_STRING,
#                 description="Company sort: new, old, most_products, most_ordered",
#             ),
#             openapi.Parameter(
#                 name="is_popular",
#                 in_=openapi.IN_QUERY,
#                 description="Filter products by is_popular",
#                 type=openapi.TYPE_BOOLEAN,
#             ),
#         ],
#         operation_description="Download public companies as Excel file",
#     )
#     def get(self, request, *args, **kwargs):
#         return CompanyService(request=request).get_public_companies_excel(
#             *args,
#             **kwargs,
#         )

class CompanyIndustriesListView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        tags=["Company"],
        manual_parameters=[
            openapi.Parameter(
                name="search",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Company Search by name",
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        return CompanyService(request=request).get_company_industries(*args, **kwargs)

class CompanyRegionsListView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        tags=["Company"],
        manual_parameters=[
            openapi.Parameter(
                name="search",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Company Search by name",
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        return CompanyService(request=request).get_company_regions(*args, **kwargs)
