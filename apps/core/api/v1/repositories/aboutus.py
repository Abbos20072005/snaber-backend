from apps.core.models import AboutUs


class AboutUsRepository:
    def get_about_us(self):
        return AboutUs.objects.first()
