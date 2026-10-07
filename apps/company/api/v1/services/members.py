from rest_framework import status

from apps.company.api.v1.repositories.members import CompanyMemberRepository
from apps.company.api.v1.serializers.members import (
    CompanyMemberCreateSerializer,
    CompanyMemberSerializer,
)
from apps.core.services import BaseService


class CompanyMemberService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = CompanyMemberRepository()

    def get_members(self, *args, **kwargs):
        company = self.request.company
        members = self.db.get_members(company=company)
        return self.get_paginated_response(
            members,
            CompanyMemberSerializer,
            context={"request": self.request},
        )

    def get_member(self, *args, **kwargs):
        company = self.request.company
        member = self.db.get_member(member_id=kwargs.get("id"), company=company)
        return self.get_response_object(
            member,
            CompanyMemberSerializer,
            context={"request": self.request},
        )

    def create_member(self, *args, **kwargs):
        company = self.request.company
        serializer = CompanyMemberCreateSerializer(
            data=self.request.data,
            context={"request": self.request, "company": company},
        )
        serializer.is_valid(raise_exception=True)
        member = serializer.save()
        return self.get_response_object(
            member,
            CompanyMemberSerializer,
            context={"request": self.request},
            status_code=status.HTTP_201_CREATED,
        )

    def delete_member(self, *args, **kwargs):
        company = self.request.company
        member = self.db.get_member(member_id=kwargs.get("id"), company=company)
        self.db.delete_member(member)
        return self.get_response_object(
            context={"request": self.request},
            status_code=status.HTTP_204_NO_CONTENT,
        )
