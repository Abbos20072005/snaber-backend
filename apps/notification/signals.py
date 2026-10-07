from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail

from apps.authentication.models import User
# Chat center notifications are disabled for the frontend
# from apps.chat.models import Conversation, Message
from apps.company.models import Company, CompanyMember
from apps.notification.api.v1.repositories.notifications import NotificationRepository
from apps.notification.models import Notification
from apps.order.models import Order
from apps.product.models import Product


def send_notification_email(user, subject, message):
    if user and user.email:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "EMAIL_HOST_USER", None),
            recipient_list=[user.email],
            fail_silently=True,
        )


@receiver(post_save, sender=Product)
def product_created_notification(sender, instance, created, **kwargs):
    if created and instance.owner:
        for member in instance.owner.members.all():
            NotificationRepository().create_notification(
                user=member.user,
                title_uz="Mahsulot yaratildi",
                title_ru="Продукт создан",
                title_en="Product Created",
                message_uz=f"Mahsulot {instance.name_uz} muvaffaqiyatli yaratildi.",
                message_ru=f"Продукт {instance.name_ru} успешно создан.",
                message_en=f"Product {instance.name_en} has been successfully created.",
                notification_type=Notification.NotificationType.PRODUCT,
                redirect_id=instance.id,
            )
            send_notification_email(
                member.user,
                "Product Created",
                f"Product {instance.name_en} has been successfully created.",
            )


@receiver(post_save, sender=Order)
def order_created_notification(sender, instance, created, **kwargs):
    if created:
        for member in instance.company.members.select_related("user"):
            NotificationRepository().create_notification(
                user=member.user,
                title_uz="Yangi buyurtma",
                title_ru="Новый заказ",
                title_en="New Order",
                message_uz=f"#{instance.id} - yangi buyurtma qabul qilindi.",
                message_ru=f"Новый заказ №{instance.id} размещен.",
                message_en=f"New order #{instance.id} has been placed.",
                notification_type=Notification.NotificationType.ORDER,
                redirect_id=instance.id,
            )
            send_notification_email(
                member.user,
                "New Order",
                f"New order #{instance.id} has been placed.",
            )


# Chat center (message notifications) is disabled for the frontend
# @receiver(post_save, sender=Message)
# def message_sent_notification(sender, instance, created, **kwargs):
#     if created and not instance.system_message:
#         conversation = instance.conversation
#         if conversation.buyer and conversation.seller:
#             recipient = (
#                 conversation.seller
#                 if instance.sender == conversation.buyer
#                 else conversation.buyer
#             )
#             NotificationRepository().create_notification(
#                 user=recipient,
#                 title_uz="Yangi xabar",
#                 title_ru="Новое сообщение",
#                 title_en="New Message",
#                 message_uz=f"Sizda #{conversation.id} - suhbatda yangi xabar bor.",
#                 message_ru=f"У вас новое сообщение в беседе №{conversation.id}.",
#                 message_en=f"You have a new message in conversation #{conversation.id}.",
#                 notification_type=Notification.NotificationType.CHAT,
#                 redirect_id=conversation.id,
#             )
#             send_notification_email(
#                 recipient,
#                 "New Message",
#                 f"You have a new message in conversation #{conversation.id}.",
#             )


# Chat center (conversation notifications) is disabled for the frontend
# @receiver(post_save, sender=Conversation)
# def conversation_created_notification(sender, instance, created, **kwargs):
#     if created:
#         seller = instance.seller
#         if not seller and instance.product_variant:
#             first_member = (
#                 instance.product_variant.product.owner.members.select_related(
#                     "user"
#                 ).first()
#             )
#             if first_member:
#                 seller = first_member.user
#         if seller and instance.buyer:
#             NotificationRepository().create_notification(
#                 user=seller,
#                 title_uz="Yangi suhbat",
#                 title_ru="Новый чат",
#                 title_en="New Conversation",
#                 message_uz=f"Xaridor {instance.buyer.full_name} siz bilan suhbat boshladi.",
#                 message_ru=f"Покупатель {instance.buyer.full_name} начал с вами чат.",
#                 message_en=f"Buyer {instance.buyer.full_name} started a conversation with you.",
#                 notification_type=Notification.NotificationType.CHAT,
#                 redirect_id=instance.id,
#             )
#             send_notification_email(
#                 seller,
#                 "New Conversation",
#                 f"Buyer {instance.buyer.full_name} started a conversation with you.",
#             )


@receiver(post_save, sender=Company)
def company_created_notification(sender, instance, created, **kwargs):
    if created:
        moderators = User.objects.filter(
            role__in=[User.Roles.MODERATOR, User.Roles.ADMIN, User.Roles.SUPER_ADMIN]
        )
        for moderator in moderators:
            NotificationRepository().create_notification(
                user=moderator,
                title_uz="Yangi kompaniya ro'yxatdan o'tdi",
                title_ru="Новая регистрация компании",
                title_en="New Company Registration",
                message_uz=f"'{instance.name_uz}' nomli yangi kompaniya ro'yxatdan o'tdi va tekshirishni kutmoqda.",
                message_ru=f"Новая компания '{instance.name_ru}' зарегистрирована и ожидает проверки.",
                message_en=f"A new company '{instance.name_en}' has been registered and is pending review.",
                notification_type=Notification.NotificationType.COMPANY,
                redirect_id=instance.id,
            )
            send_notification_email(
                moderator,
                "New Company Registration",
                f"A new company {instance.name_en} has been registered and is pending review.",
            )


@receiver(post_save, sender=CompanyMember)
def company_member_added_notification(sender, instance, created, **kwargs):
    if created:
        NotificationRepository().create_notification(
            user=instance.user,
            title_uz="Kompaniyaga xush kelibsiz",
            title_ru="Добро пожаловать в компанию",
            title_en="Welcome to Company",
            message_uz=f"Siz '{instance.company.name_uz}' kompaniyasiga a'zo sifatida qo'shildingiz.",
            message_ru=f"Вы были добавлены как участник '{instance.company.name_ru}'.",
            message_en=f"You have been added as a member of '{instance.company.name_en}'.",
            notification_type=Notification.NotificationType.COMPANY,
            redirect_id=instance.company_id,
        )
        send_notification_email(
            instance.user,
            "Welcome to Company",
            f"You have been added as a member of {instance.company.name_en}.",
        )

