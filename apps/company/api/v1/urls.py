from django.urls import path

from apps.company.api.v1.views.certificates import (
    CompanyCertificateCreateView,
    CompanyCertificateDetailUpdateDeleteView,
    CompanyCertificateListView,
)
from apps.company.api.v1.views.companies import (
    CompanyCreateListView,
    CompanyDetailUpdateDeleteView,
    # Company mini-site (public company page) is disabled for the frontend
    # CompanyProductView,
    # CompanyStatisticsView,
    # DraftCompaniesView,
    # DraftCompanyDetailView,
    # PublicCompanyDetailView,
    # PublicCompanyExcelView,
    # PublicCompanyListView,
    RegionListView,
    SellerCompanyView, CompanyIndustriesListView, CompanyRegionsListView,
)
from apps.company.api.v1.views.galleries import (
    CompanyGalleryCreateView,
    CompanyGalleryDetailUpdateDeleteView,
    CompanyGalleryListView,
)
from apps.company.api.v1.views.members import (
    CompanyMemberCreateListView,
    CompanyMemberDetailDeleteView,
)

urlpatterns = [
    path(
        "",
        CompanyCreateListView.as_view(),
        name="company-list",
    ),
    # Company mini-site (statistics) is disabled for the frontend
    # path(
    #     "statistics/",
    #     CompanyStatisticsView.as_view(),
    #     name="company-statistics",
    # ),
    path(
        "<int:id>/",
        CompanyDetailUpdateDeleteView.as_view(),
        name="company-detail",
    ),
    # Company mini-site (company products page) is disabled for the frontend
    # path(
    #     "<int:id>/product/",
    #     CompanyProductView.as_view(),
    #     name="company-product",
    # ),
    path(
        "seller/",
        SellerCompanyView.as_view(),
        name="seller-company",
    ),
    path(
        "certificate/",
        CompanyCertificateCreateView.as_view(),
        name="company-certificate",
    ),
    path(
        "certificate/<int:id>/",
        CompanyCertificateDetailUpdateDeleteView.as_view(),
        name="company-certificate-detail",
    ),
    path(
        "certificates/<int:id>/",
        CompanyCertificateListView.as_view(),
        name="company-certificate-list",
    ),
    path(
        "gallery/",
        CompanyGalleryCreateView.as_view(),
        name="company-gallery",
    ),
    path(
        "gallery/<int:id>/",
        CompanyGalleryDetailUpdateDeleteView.as_view(),
        name="company-gallery-detail",
    ),
    path(
        "galleries/<int:id>/",
        CompanyGalleryListView.as_view(),
        name="company-gallery-list",
    ),
    path(
        "region/",
        RegionListView.as_view(),
        name="region-list",
    ),
    # Company draft moderation (status + moderator comment) is disabled for the frontend
    # path(
    #     "draft/",
    #     DraftCompaniesView.as_view(),
    #     name="draft-companies",
    # ),
    # path(
    #     "draft/<int:id>/",
    #     DraftCompanyDetailView.as_view(),
    #     name="draft-company-patch",
    # ),
    # Company mini-site (public company page) is disabled for the frontend
    # path(
    #     "public/<int:id>/",
    #     PublicCompanyDetailView.as_view(),
    #     name="public-company-detail",
    # ),
    # path(
    #     "public/excel/",
    #     PublicCompanyExcelView.as_view(),
    #     name="public-company-excel",
    # ),
    # path(
    #     "public/",
    #     PublicCompanyListView.as_view(),
    #     name="public-company-list",
    # ),
    path(
        "members/",
        CompanyMemberCreateListView.as_view(),
        name="company-members",
    ),
    path(
        "members/<int:id>/",
        CompanyMemberDetailDeleteView.as_view(),
        name="company-members-detail",
    ),
    path(
        "industries/",
        CompanyIndustriesListView.as_view(),
        name="company-industries",
    ),
    path(
        "regions/",
        CompanyRegionsListView.as_view(),
        name="company-regions",
    )
]

