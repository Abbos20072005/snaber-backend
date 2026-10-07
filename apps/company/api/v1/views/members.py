from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.company.api.v1.serializers.members import (
    CompanyMemberCreateSerializer,
    CompanyMemberSerializer,
)
from apps.company.api.v1.services.members import CompanyMemberService
from apps.core.permissions import CanManageMembers, IsCompanyMember


class CompanyMemberCreateListView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsCompanyMember(), CanManageMembers()]
        return [IsAuthenticated(), IsCompanyMember()]

    @swagger_auto_schema(
        responses={200: CompanyMemberSerializer(many=True)},
        tags=["Company Members"],
        operation_description="Get list of company members",
    )
    def get(self, request, *args, **kwargs):
        return CompanyMemberService(request=request).get_members(*args, **kwargs)

    @swagger_auto_schema(
        request_body=CompanyMemberCreateSerializer,
        responses={201: CompanyMemberSerializer},
        tags=["Company Members"],
        operation_description="Add a new member to the company",
    )
    def post(self, request, *args, **kwargs):
        return CompanyMemberService(request=request).create_member(*args, **kwargs)


class CompanyMemberDetailDeleteView(APIView):
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsCompanyMember(), CanManageMembers()]
        return [IsAuthenticated(), IsCompanyMember()]

    @swagger_auto_schema(
        responses={200: CompanyMemberSerializer},
        tags=["Company Members"],
        operation_description="Get company member detail",
    )
    def get(self, request, *args, **kwargs):
        return CompanyMemberService(request=request).get_member(*args, **kwargs)

    @swagger_auto_schema(
        responses={204: "No Content"},
        tags=["Company Members"],
        operation_description="Remove a member from the company",
    )
    def delete(self, request, *args, **kwargs):
        return CompanyMemberService(request=request).delete_member(*args, **kwargs)
