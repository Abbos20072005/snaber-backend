from django.db.models import Count

from apps.authentication.models import User
from apps.company.api.v1.filters.companies import RegionFilter, IndustryFilter
from apps.company.models import Company, CompanyMember, Region, Industry
from apps.core.exceptions import ObjectNotFoundException
from apps.product.models import Product


class CompanyRepository:
    def __init__(self, request=None):
        self.request = request

    def get_companies(self):
        return Company.objects.annotate(
            order_counts=Count("company_orders", distinct=True),
            member_counts=Count("members", distinct=True),
        )

    def get_company_statistics(self):
        return {
            "companies": Company.objects.count(),
            "products": Product.objects.count(),
            "users": User.objects.count(),
        }

    def get_company(self, company_id):
        member = CompanyMember.objects.filter(
            company_id=company_id,
            user=self.request.user,
        ).first()

        if not member:
            raise ObjectNotFoundException(
                message="Company not found",
                message_key="company_not_found",
            )
        company = (
            Company.objects.prefetch_related(
                "certificates",
                "gallery",
            )
            .filter(id=company_id)
            .first()
        )
        if not company:
            raise ObjectNotFoundException(
                message="Company not found",
                message_key="company_not_found",
            )
        return company

    def get_company_products(self, company_id):
        if not Company.objects.filter(id=company_id).exists():
            raise ObjectNotFoundException(
                message="Company not found",
                message_key="company_not_found",
            )

        product = Product.objects.filter(owner_id=company_id, is_active=True)
        return product

    def get_seller_company(self, user):
        if user.role != "seller":
            raise ObjectNotFoundException(
                message="User not a seller",
                message_key="user_not_seller",
            )

        member = (
            CompanyMember.objects.filter(user=user).select_related("company").first()
        )
        if not member:
            raise ObjectNotFoundException(
                message="Company not found",
                message_key="company_not_found",
            )
        return member.company

    def get_regions(self):
        regions = RegionFilter(self.request.query_params, queryset=Region.objects.all()).qs
        return regions

    def get_draft_company(self, company_id):
        company = Company.objects.filter(id=company_id).first()
        if not company:
            raise ObjectNotFoundException(
                message="Company not found",
                message_key="company_not_found",
            )
        return company

    def get_public_company(self, company_id):
        company = Company.objects.filter(
            status=Company.CompanyStatus.ACTIVE,
            id=company_id,
        ).first()
        if not company:
            raise ObjectNotFoundException(
                message="Company not found",
                message_key="company_not_found",
            )
        return company

    def get_public_companies(self):
        return Company.objects.filter(status=Company.CompanyStatus.ACTIVE).annotate(
            order_counts=Count("company_orders", distinct=True),
            member_counts=Count("members", distinct=True),
        )


    def get_industries(self):
        industry = IndustryFilter(self.request.query_params, queryset=Industry.objects.all()).qs
        return industry

    def get_region(self):
        return Region.objects.all()