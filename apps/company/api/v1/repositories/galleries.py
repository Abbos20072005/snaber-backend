from apps.company.models import Company, CompanyGallery
from apps.core.exceptions import ObjectNotFoundException


class CompanyGalleryRepository:
    def get_galleries(self):
        return CompanyGallery.objects.all()

    def get_gallery(self, gallery_id):
        gallery = CompanyGallery.objects.filter(id=gallery_id).first()
        if not gallery:
            raise ObjectNotFoundException(
                message="CompanyGallery not found",
                message_key="company_gallery_not_found",
            )
        return gallery

    def get_company_gallery(self, company_id):
        if not Company.objects.filter(id=company_id).exists():
            raise ObjectNotFoundException(
                message="Company not found",
                message_key="company_not_found",
            )
        gallery = CompanyGallery.objects.filter(company_id=company_id)
        return gallery
