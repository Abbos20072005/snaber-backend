from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.notification.api.v1.serializers.notifications import (
    NotificationsListSerializer,
)
from apps.notification.api.v1.services.notifications import NotificationService


class NotificationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: NotificationsListSerializer(many=True)},
        tags=["Notification"],
        operation_description="API to list user notifications",
    )
    def get(self, request, *args, **kwargs):
        return NotificationService(request=request).list_notifications(*args, **kwargs)

    @swagger_auto_schema(
        responses={200: NotificationsListSerializer(many=True)},
        tags=["Notification"],
        operation_description="API to delete all notifications",
    )
    def delete(self, request, *args, **kwargs):
        return NotificationService(request=request).delete_all_notifications(
            *args, **kwargs
        )


class NotificationMarkReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: "Notification marked as read."},
        tags=["Notification"],
        operation_description="API to mark a specific notification as read",
    )
    def post(self, request, *args, **kwargs):
        return NotificationService(request=request).mark_as_read(*args, **kwargs)


class NotificationMarkAllReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: "All notifications marked as read."},
        tags=["Notification"],
        operation_description="API to mark all user notifications as read",
    )
    def post(self, request, *args, **kwargs):
        return NotificationService(request=request).mark_all_as_read(*args, **kwargs)


class NotificationUnreadCountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Notification"],
        operation_description="API to get unread notifications count",
    )
    def get(self, request, *args, **kwargs):
        return NotificationService(request=request).get_unread_count(*args, **kwargs)


class NotificationDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={204: "Notification deleted.", 404: "Notification not found."},
        tags=["Notification"],
        operation_description="API to delete a specific notification",
    )
    def delete(self, request, *args, **kwargs):
        return NotificationService(request=request).delete_notification(*args, **kwargs)
