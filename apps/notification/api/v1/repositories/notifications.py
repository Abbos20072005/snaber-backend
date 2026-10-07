from apps.notification.models import Notification


class NotificationRepository:
    def get_user_notifications(self, user):
        return Notification.objects.filter(user=user).order_by("-created_at")

    def get_unread_count(self, user):
        return Notification.objects.filter(user=user, is_read=False).count()

    def mark_as_read(self, user, notification_id):
        return Notification.objects.filter(user=user, id=notification_id).update(
            is_read=True
        )

    def mark_all_as_read(self, user):
        return Notification.objects.filter(user=user, is_read=False).update(
            is_read=True
        )

    def create_notification(
        self,
        user,
        title_uz,
        title_ru,
        title_en,
        message_uz,
        message_ru,
        message_en,
        notification_type=Notification.NotificationType.OTHER,
        redirect_id=None,
    ):
        return Notification.objects.create(
            user=user,
            title_uz=title_uz,
            title_ru=title_ru,
            title_en=title_en,
            message_uz=message_uz,
            message_ru=message_ru,
            message_en=message_en,
            notification_type=notification_type,
            redirect_id=redirect_id,
        )

    def delete_notification(self, user, notification_id):
        deleted_count, _ = Notification.objects.filter(
            user=user, id=notification_id
        ).delete()
        return deleted_count

    def delete_all_notifications(self, user):
        return Notification.objects.filter(user=user).delete()
