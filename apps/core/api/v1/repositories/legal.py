from apps.core.models import LegalClientsInfo


class LegalClientsInfoRepository:
    def get_legal_info(self):
        return LegalClientsInfo.objects.first()
