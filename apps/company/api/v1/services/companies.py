# from io import BytesIO

# from django.http import HttpResponse
# from django.utils import timezone
# from openpyxl import Workbook
# from openpyxl.styles import Font, PatternFill
# from openpyxl.utils import get_column_letter
from rest_framework import status

# Company list / mini-site / draft moderation (disabled for the frontend)
# from apps.company.api.v1.filters.companies import CompanyDraftFilter, CompanyFilter, IndustryFilter, RegionFilter
from apps.company.api.v1.repositories.companies import CompanyRepository
from apps.company.api.v1.serializers.companies import (
    CompanyCreateSerializer,
    CompanyDetailListSerializer,
    # CompanyListSerializer,
    # CompanyStatisticsSerializer,
    CompanyUpdateSerializer,
    # DraftCompanySerializer,
    RegionListSerializer, CompanyIndustriesSerializer, CompanyRegionSerializer,
)
from apps.core.services import BaseService, ViewService
# Company draft moderation (disabled for the frontend)
# from apps.company.models import Company as CompanyModel
# from apps.notification.api.v1.repositories.notifications import NotificationRepository
# from apps.notification.models import Notification
# from apps.product.api.v1.filters.products import ProductDynamicFilter
# from apps.product.api.v1.serializers.products import (
#     CompanyProductListSerializer,
# )


class CompanyService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = CompanyRepository(request=request)

    # Company list (Список компаний) is disabled for the frontend
    # def get_companies(self, *args, **kwargs):
    #     companies = self.db.get_companies()
    #     return self.get_response(
    #         companies,
    #         CompanyListSerializer,
    #         context={"request": self.request},
    #         many=True,
    #     )

    # Company mini-site (statistics) is disabled for the frontend
    # def get_company_statistics(self, *args, **kwargs):
    #     company = self.db.get_company_statistics()
    #     return self.get_response(
    #         company,
    #         CompanyStatisticsSerializer,
    #         context={"request": self.request},
    #     )

    def get_company(self, *args, **kwargs):
        company = self.db.get_company(company_id=kwargs.get("id"))
        ViewService().register_view(self.request, company)
        return self.get_response_object(
            company,
            CompanyDetailListSerializer,
            context={"request": self.request},
        )

    def create_company(self, *args, **kwargs):
        serializer = CompanyCreateSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        company = serializer.save()
        return self.get_response_object(
            company,
            CompanyDetailListSerializer,
            context={"request": self.request},
        )

    def delete_company(self, *args, **kwargs):
        company = self.db.get_company(company_id=kwargs.get("id"))
        company.delete()
        return self.get_response_object(
            context={"request": self.request},
            status_code=status.HTTP_204_NO_CONTENT,
        )

    def update_company(self, *args, **kwargs):
        company = self.db.get_company(company_id=kwargs.get("id"))
        serializer = CompanyUpdateSerializer(
            data=self.request.data,
            context={"request": self.request},
            partial=True,
            instance=company,
        )
        serializer.is_valid(raise_exception=True)
        new_company = serializer.save()
        return self.get_response_object(
            new_company, CompanyDetailListSerializer, context={"request": self.request}
        )

    # Company mini-site (company products page) is disabled for the frontend
    # def get_company_products(self, *args, **kwargs):
    #     product = self.db.get_company_products(company_id=kwargs.get("id"))
    #     product = ProductDynamicFilter(
    #         data=self.request.query_params,
    #         queryset=product,
    #         request=self.request,
    #     ).qs
    #     return self.get_paginated_response(
    #         product,
    #         CompanyProductListSerializer,
    #         context={"request": self.request},
    #     )

    def get_seller_company(self, *args, **kwargs):
        company = self.db.get_seller_company(user=self.request.user)
        return self.get_response_object(
            company,
            CompanyDetailListSerializer,
            context={"request": self.request},
        )

    def get_regions(self, *args, **kwargs):
        regions = self.db.get_regions()
        return self.get_response(
            regions,
            RegionListSerializer,
            context={"request": self.request},
            many=True,
        )

    # Company draft moderation (status + moderator comment) is disabled for the frontend
    # def get_draft_companies(self, *args, **kwargs):
    #     company = self.db.get_companies()
    #     companies = CompanyDraftFilter(self.request.query_params, queryset=company).qs
    #     return self.get_paginated_response(
    #         companies,
    #         CompanyListSerializer,
    #         context={"request": self.request},
    #     )

    # def update_draft_company(self, *args, **kwargs):
    #     company = self.db.get_draft_company(company_id=kwargs.get("id"))
    #     old_status = company.status
    #     serializer = DraftCompanySerializer(
    #         data=self.request.data,
    #         instance=company,
    #         partial=True,
    #         context={"request": self.request},
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     new_company = serializer.save()
    #
    #     new_status = new_company.status
    #     if new_status != old_status:
    #         for member in new_company.members.select_related("user"):
    #             reason = new_company.description_moderator
    #             reason_suffix_uz = f" Sabab: {reason}" if reason else ""
    #             reason_suffix_ru = f" Причина: {reason}" if reason else ""
    #             reason_suffix_en = f" Reason: {reason}" if reason else ""
    #
    #             if new_status == CompanyModel.CompanyStatus.ACTIVE:
    #                 title_uz = "Kompaniya tasdiqlandi"
    #                 title_ru = "Компания одобрена"
    #                 title_en = "Company Approved"
    #                 message_uz = f"'{new_company.name_uz}' kompaniyangiz tasdiqlandi va faol holatga o'tkazildi.{reason_suffix_uz}"
    #                 message_ru = f"Ваша компания '{new_company.name_ru}' одобрена и теперь активна.{reason_suffix_ru}"
    #                 message_en = f"Your company '{new_company.name_en}' has been approved and is now active.{reason_suffix_en}"
    #             elif new_status == CompanyModel.CompanyStatus.INACTIVE:
    #                 title_uz = "Kompaniya faolsizlantirildi"
    #                 title_ru = "Компания деактивирована"
    #                 title_en = "Company Deactivated"
    #                 message_uz = f"'{new_company.name_uz}' kompaniyangiz faolsizlantirildi.{reason_suffix_uz}"
    #                 message_ru = f"Ваша компания '{new_company.name_ru}' деактивирована.{reason_suffix_ru}"
    #                 message_en = f"Your company '{new_company.name_en}' has been set to inactive.{reason_suffix_en}"
    #             elif new_status == CompanyModel.CompanyStatus.BLOCKED:
    #                 title_uz = "Kompaniya bloklandi"
    #                 title_ru = "Компания заблокирована"
    #                 title_en = "Company Blocked"
    #                 message_uz = f"'{new_company.name_uz}' kompaniyangiz bloklandi.{reason_suffix_uz}"
    #                 message_ru = f"Ваша компания '{new_company.name_ru}' заблокирована.{reason_suffix_ru}"
    #                 message_en = f"Your company '{new_company.name_en}' has been blocked.{reason_suffix_en}"
    #             else:
    #                 continue
    #
    #             NotificationRepository().create_notification(
    #                 user=member.user,
    #                 title_uz=title_uz,
    #                 title_ru=title_ru,
    #                 title_en=title_en,
    #                 message_uz=message_uz,
    #                 message_ru=message_ru,
    #                 message_en=message_en,
    #                 notification_type=Notification.NotificationType.COMPANY,
    #                 redirect_id=new_company.id,
    #             )
    #
    #     return self.get_response_object(
    #         new_company, DraftCompanySerializer, context={"request": self.request}
    #     )

    # Company mini-site (public company page) is disabled for the frontend
    # def get_public_company(self, *args, **kwargs):
    #     company = self.db.get_public_company(company_id=kwargs.get("id"))
    #     ViewService().register_view(self.request, company)
    #     return self.get_response_object(
    #         company,
    #         CompanyDetailListSerializer,
    #         context={"request": self.request},
    #     )

    # def get_public_companies(self, *args, **kwargs):
    #     companies = self.db.get_public_companies()
    #     companies = CompanyFilter(self.request.query_params, queryset=companies).qs
    #     return self.get_paginated_response(
    #         companies,
    #         CompanyListSerializer,
    #         context={"request": self.request},
    #     )

    # def get_public_companies_excel(self, *args, **kwargs):
    #     companies = self.db.get_public_companies()
    #     companies = CompanyFilter(self.request.query_params, queryset=companies).qs
    #     companies = companies.select_related("region").prefetch_related("industries")
    #
    #     workbook = Workbook()
    #     sheet = workbook.active
    #     sheet.title = "Public Companies"
    #
    #     headers = [
    #         "Name",
    #         "Region",
    #         "Industries",
    #         "Phone",
    #         "Email",
    #         "Telegram",
    #         "YouTube",
    #         "Instagram",
    #         "Facebook",
    #         "WhatsApp",
    #         "Website",
    #         "Orders count",
    #     ]
    #     sheet.append(headers)
    #
    #     header_fill = PatternFill(
    #         fill_type="solid",
    #         start_color="1F4E78",
    #         end_color="1F4E78",
    #     )
    #     for cell in sheet[1]:
    #         cell.font = Font(bold=True, color="FFFFFF")
    #         cell.fill = header_fill
    #
    #     for company in companies:
    #         sheet.append(
    #             [
    #                 company.name,
    #                 company.region.name if company.region else "",
    #                 ", ".join(industry.name for industry in company.industries.all()),
    #                 company.phone,
    #                 company.email,
    #                 company.telegram,
    #                 company.youtube,
    #                 company.instagram,
    #                 company.facebook,
    #                 company.whatsapp,
    #                 company.own_site,
    #                 getattr(company, "order_counts", 0),
    #             ]
    #         )
    #
    #     for column_cells in sheet.columns:
    #         max_length = max(
    #             len(str(cell.value)) if cell.value is not None else 0
    #             for cell in column_cells
    #         )
    #         column_letter = get_column_letter(column_cells[0].column)
    #         sheet.column_dimensions[column_letter].width = min(max_length + 2, 50)
    #
    #     output = BytesIO()
    #     workbook.save(output)
    #     output.seek(0)
    #
    #     filename = timezone.now().strftime("public_companies_%Y%m%d_%H%M%S.xlsx")
    #     response = HttpResponse(
    #         output.getvalue(),
    #         content_type=(
    #             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    #         ),
    #     )
    #     response["Content-Disposition"] = f'attachment; filename="{filename}"'
    #     return response

    def get_company_industries(self, *args, **kwargs):
        industry = self.db.get_industries()
        return self.get_paginated_response(
            industry,
            CompanyIndustriesSerializer,
            context={"request": self.request},
        )

    def get_company_regions(self, *args, **kwargs):
        region = self.db.get_regions()
        return self.get_paginated_response(
            region,
            CompanyRegionSerializer,
            context={"request": self.request},
        )
