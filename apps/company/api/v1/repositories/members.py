from apps.company.models import CompanyMember
from apps.core.exceptions import ObjectNotFoundException


class CompanyMemberRepository:
    def get_members(self, company):
        return CompanyMember.objects.filter(company=company).select_related("user")

    def get_member(self, member_id, company):
        member = (
            CompanyMember.objects.filter(id=member_id, company=company)
            .select_related("user")
            .first()
        )
        if not member:
            raise ObjectNotFoundException(
                message="Company member not found",
                message_key="company_member_not_found",
            )
        return member

    def create_member(self, user, company):
        return CompanyMember.objects.create(
            user=user,
            company=company,
            is_owner=False,
        )

    def delete_member(self, member):
        member.delete()
