from rest_framework import status
from rest_framework.response import Response

from apps.core.services import BaseService
from apps.notification.api.v1.repositories.notifications import NotificationRepository
from apps.notification.api.v1.serializers.notifications import (
    NotificationsListSerializer,
)


class NotificationService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = NotificationRepository()

    def list_notifications(self, *args, **kwargs):
        notifications = self.db.get_user_notifications(self.request.user)
        return self.get_paginated_response(
            queryset=notifications,
            response_serializer_class=NotificationsListSerializer,
            context={"request": self.request},
        )

    def mark_as_read(self, *args, **kwargs):
        notification_id = kwargs.get("id")
        updated = self.db.mark_as_read(self.request.user, notification_id)
        if updated:
            return Response(
                {"detail": "Notification marked as read."}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "Notification not found or already read."},
            status=status.HTTP_404_NOT_FOUND,
        )

    def mark_all_as_read(self, *args, **kwargs):
        count = self.db.mark_all_as_read(self.request.user)
        return Response(
            {"detail": f"{count} notifications marked as read."},
            status=status.HTTP_200_OK,
        )

    def get_unread_count(self, *args, **kwargs):
        count = self.db.get_unread_count(self.request.user)
        return Response({"unread_count": count}, status=status.HTTP_200_OK)

    def delete_notification(self, *args, **kwargs):
        notification_id = kwargs.get("id")
        deleted_count = self.db.delete_notification(self.request.user, notification_id)
        if not deleted_count:
            return Response(
                {"detail": "Notification not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete_all_notifications(self, *args, **kwargs):
        deleted_notifications = self.db.delete_all_notifications(self.request.user)
        if not deleted_notifications:
            return Response(
                {"detail": "Notification not found."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
