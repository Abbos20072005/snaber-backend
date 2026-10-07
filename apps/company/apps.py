from django.apps import AppConfig


class CompanyConfig(AppConfig):
    name = 'apps.company'

    def ready(self):
        import apps.company.signals  # noqa: F401
