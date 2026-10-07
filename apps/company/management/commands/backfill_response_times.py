# Chat center (response time backfill) is disabled for the frontend
# from collections import defaultdict
#
# from django.core.management.base import BaseCommand
# from django.db.models import Min, Max
#
# from apps.chat.models import Conversation, Message
# from apps.company.models import Company, CompanyMember, ResponseTimeEntry
#
#
# class Command(BaseCommand):
#     def handle(self, *args, **options):
#         self.stdout.write("Starting response time backfill...")
#
#         conversations = Conversation.objects.filter(
#             buyer__isnull=False,
#             seller__isnull=False,
#         ).iterator()
#
#         total_entries = 0
#         company_batch = defaultdict(list)
#
#         for conversation in conversations:
#             company = self._get_conversation_company(conversation)
#             if not company:
#                 continue
#
#             messages = (
#                 Message.objects.filter(
#                     conversation=conversation,
#                     system_message__isnull=True,
#                 )
#                 .select_related("sender")
#                 .order_by("created_at")
#             )
#
#             last_buyer_msg = None
#
#             for msg in messages:
#                 if msg.sender_id == conversation.buyer_id:
#                     last_buyer_msg = msg
#                 elif msg.sender_id == conversation.seller_id and last_buyer_msg:
#                     if ResponseTimeEntry.objects.filter(
#                         buyer_message=last_buyer_msg,
#                     ).exists():
#                         continue
#
#                     delta = msg.created_at - last_buyer_msg.created_at
#                     response_seconds = int(delta.total_seconds())
#                     if response_seconds < 1:
#                         continue
#
#                     ResponseTimeEntry.objects.create(
#                         company=company,
#                         conversation=conversation,
#                         buyer_message=last_buyer_msg,
#                         responded_at=msg.created_at,
#                         response_time_seconds=response_seconds,
#                     )
#                     company_batch[company.id].append(response_seconds)
#                     total_entries += 1
#
#                     last_buyer_msg = None
#
#         self._update_all_companies(company_batch)
#
#         self.stdout.write(
#             self.style.SUCCESS(
#                 f"Backfill complete. Created {total_entries} response time entries "
#                 f"for {len(company_batch)} companies."
#             )
#         )
#
#     def _update_all_companies(self, company_batch):
#         for company_id in company_batch:
#             stats = (
#                 ResponseTimeEntry.objects.filter(company_id=company_id)
#                 .aggregate(
#                     min_time=Min("response_time_seconds"),
#                     max_time=Max("response_time_seconds"),
#                 )
#             )
#
#             Company.objects.filter(id=company_id).update(
#                 min_answer_time=stats["min_time"],
#                 max_answer_time=stats["max_time"],
#             )
#
#     def _get_conversation_company(self, conversation):
#         if conversation.order_id:
#             return conversation.order.company
#         if conversation.product_variant_id:
#             variant = conversation.product_variant
#             if variant and variant.product_id:
#                 return variant.product.owner
#         member = (
#             CompanyMember.objects.filter(user=conversation.seller)
#             .select_related("company")
#             .first()
#         )
#         return member.company if member else None
