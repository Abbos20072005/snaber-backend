from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import IsBuyer
from apps.review.api.v1.serializers.comments import (
    CommentCreateSerializer,
    CommentListSerializer,
    CommentStatusSerializer,
    CommentUpdateSerializer,
)
from apps.review.api.v1.services.comments import CommentService


class CommentListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsBuyer()]
        return [AllowAny()]
    
    @swagger_auto_schema(
        responses={200: CommentListSerializer(many=True)},
        tags=["Comment"],
        operation_description="API to list comments. "
        "Use ?product=<id> or ?variant=<id> to filter.",
        manual_parameters=[
            openapi.Parameter(
                name="variant",
                in_=openapi.IN_QUERY,
                description="Filter comments by variant ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                name="product",
                in_=openapi.IN_QUERY,
                description="Filter comments by product ID (all variants)",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return CommentService(request=request).get_product_comments(*args, **kwargs)

    @swagger_auto_schema(
        responses={201: CommentListSerializer},
        request_body=CommentCreateSerializer,
        tags=["Comment"],
        operation_description="API to create a comment "
        "(only for buyers who purchased the product)",
    )
    def post(self, request, *args, **kwargs):
        return CommentService(request=request).create_comment(*args, **kwargs)


class CommentDetailUpdateDeleteView(APIView):
    @swagger_auto_schema(
        responses={200: CommentListSerializer},
        tags=["Comment"],
        operation_description="API to get a specific comment",
    )
    def get(self, request, *args, **kwargs):
        return CommentService(request=request).get_comment(*args, **kwargs)

    @swagger_auto_schema(
        responses={200: CommentListSerializer},
        request_body=CommentUpdateSerializer,
        tags=["Comment"],
        operation_description="API to update own comment",
    )
    def patch(self, request, *args, **kwargs):
        return CommentService(request=request).update_comment(*args, **kwargs)

    @swagger_auto_schema(
        responses={204: "No Content"},
        tags=["Comment"],
        operation_description="API to delete own comment",
    )
    def delete(self, request, *args, **kwargs):
        return CommentService(request=request).delete_comment(*args, **kwargs)

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsBuyer()]


class CommentStatusView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]
        
    @swagger_auto_schema(
        responses={200: CommentStatusSerializer},
        tags=["Comment"],
        operation_description="API to check if the authenticated user "
        "can comment on a variant. Use ?variant=<id>",
        manual_parameters=[
            openapi.Parameter(
                name="variant",
                in_=openapi.IN_QUERY,
                description="Variant ID to check comment status for",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return CommentService(request=request).get_comment_status(*args, **kwargs)
