from apps.company.models import Company, CompanyCertificate
from apps.core.exceptions import ObjectNotFoundException


class CompanyCertificateRepository:
    def get_certificates(self):
        return CompanyCertificate.objects.all()

    def get_certificate(self, certificate_id):
        certificate = CompanyCertificate.objects.filter(id=certificate_id).first()
        if not certificate:
            raise ObjectNotFoundException(
                message="Certificate not found",
                message_key="certificate_not_found",
            )
        return certificate

    def get_company_certificate(self, company_id):
        if not Company.objects.filter(id=company_id).exists():
            raise ObjectNotFoundException(
                message="Company not found",
                message_key="company_not_found",
            )
        certificate = CompanyCertificate.objects.filter(company_id=company_id)
        return certificate
