from apps.core.exceptions import ObjectNotFoundException
from apps.core.models import Faq


class FaqRepository:
    def get_faqs(self):
        faqs = Faq.objects.all()
        return faqs

    def get_faq(self, faq_id):
        faq = Faq.objects.filter(id=faq_id).first()
        if not faq_id:
            raise ObjectNotFoundException(
                message="Faq not found",
                message_key="faq_not_found",
            )
        return faq
