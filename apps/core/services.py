from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.db.models import F
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.response import Response

from apps.core.models import ObjectView
from apps.core.utils import BackendPageNumberPagination


class ServiceDefaultResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Ok")
    result = serializers.JSONField(default={})


class BaseService:
    pagination_class = BackendPageNumberPagination

    def __init__(self, request):
        self.request = request
        self._paginator: BackendPageNumberPagination | None = None

    def get_response(
        self,
        obj,
        response_serializer_class=ServiceDefaultResponseSerializer,
        *,
        context: dict = None,
        many: bool = False,
        status_code: int = status.HTTP_200_OK,
    ) -> Response:
        serializer = response_serializer_class(obj, context=context or {}, many=many)
        return Response(serializer.data, status=status_code)

    def get_response_object(
        self,
        obj=None,
        response_serializer_class=ServiceDefaultResponseSerializer,
        *,
        context: dict = None,
        status_code: int = status.HTTP_200_OK,
    ) -> Response:
        serializer = response_serializer_class(obj, context=context or {})
        return Response(serializer.data, status=status_code)

    def paginate_queryset(self, queryset):
        if not self._paginator:
            self._paginator = self.pagination_class()
        return self._paginator.paginate_queryset(queryset, self.request)

    def get_paginated_response(
        self,
        queryset,
        response_serializer_class=ServiceDefaultResponseSerializer,
        *,
        context: dict = None,
        additional_data: dict = None,
    ) -> Response:
        paginated = self.paginate_queryset(queryset)
        serializer = response_serializer_class(
            paginated, many=True, context=context or {}
        )
        response = self._paginator.get_paginated_response(serializer.data)

        if additional_data:
            response.data.update(additional_data)
        return response


class ViewService:
    def register_view(self, request, obj):
        content_type = ContentType.objects.get_for_model(obj)
        user = request.user if request.user.is_authenticated else None
        ip_address = self._get_client_ip(request)

        if user:
            _, created = ObjectView.objects.get_or_create(
                content_type=content_type,
                object_id=obj.id,
                user=user,
                defaults={"ip_address": ip_address},
            )
        else:
            recent = ObjectView.objects.filter(
                content_type=content_type,
                object_id=obj.id,
                ip_address=ip_address,
                created_at__gte=timezone.now() - timedelta(hours=24),
            ).exists()
            created = False
            if not recent:
                ObjectView.objects.create(
                    content_type=content_type,
                    object_id=obj.id,
                    ip_address=ip_address,
                )
                created = True

        if created:
            obj._meta.model.objects.filter(id=obj.id).update(
                view_count=F("view_count") + 1
            )
        return created

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
