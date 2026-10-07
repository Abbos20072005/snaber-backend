from django.apps import AppConfig


class ProductConfig(AppConfig):
    name = 'apps.product'

    def ready(self):
        import apps.product.signals.categories
        import apps.product.signals.products
        import apps.product.signals.variants
