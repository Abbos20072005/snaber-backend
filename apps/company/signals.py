# Chat center (response time tracking) is disabled for the frontend
# from django.db.models import Min, Max
# from django.db.models.signals import post_save
# from django.dispatch import receiver
#
# from apps.chat.models import Message
# from apps.company.models import CompanyMember, ResponseTimeEntry
#
#
# @receiver(post_save, sender=Message)
# def track_response_time(sender, instance, created, **kwargs):
#     if not created or instance.system_message:
#         return
#
#     conversation = instance.conversation
#     if not conversation.seller or instance.sender != conversation.seller:
#         return
#
#     buyer = conversation.buyer
#     if not buyer:
#         return
#
#     company = _get_conversation_company(conversation)
#     if not company:
#         return
#
#     last_buyer_msg = (
#         Message.objects.filter(
#             conversation=conversation,
#             sender=buyer,
#             system_message__isnull=True,
#             created_at__lt=instance.created_at,
#         )
#         .order_by("-created_at")
#         .first()
#     )
#     if not last_buyer_msg:
#         return
#
#     if ResponseTimeEntry.objects.filter(buyer_message=last_buyer_msg).exists():
#         return
#
#     delta = instance.created_at - last_buyer_msg.created_at
#     response_seconds = int(delta.total_seconds())
#     if response_seconds < 1:
#         return
#
#     ResponseTimeEntry.objects.create(
#         company=company,
#         conversation=conversation,
#         buyer_message=last_buyer_msg,
#         responded_at=instance.created_at,
#         response_time_seconds=response_seconds,
#     )
#     _update_company_answer_time(company)
#
#
# def _get_conversation_company(conversation):
#     if conversation.order_id:
#         return conversation.order.company
#     if conversation.product_variant_id:
#         variant = conversation.product_variant
#         if variant and variant.product_id:
#             return variant.product.owner
#     member = (
#         CompanyMember.objects.filter(user=conversation.seller)
#         .select_related("company")
#         .first()
#     )
#     return member.company if member else None
#
#
# def _update_company_answer_time(company):
#     stats = (
#         ResponseTimeEntry.objects.filter(company=company)
#         .aggregate(
#             min_time=Min("response_time_seconds"),
#             max_time=Max("response_time_seconds"),
#         )
#     )
#
#     company.min_answer_time = stats["min_time"]
#     company.max_answer_time = stats["max_time"]
#     company.save(update_fields=["min_answer_time", "max_answer_time"])
