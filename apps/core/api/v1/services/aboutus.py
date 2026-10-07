from apps.core.api.v1.repositories.aboutus import AboutUsRepository
from apps.core.api.v1.serializers.aboutus import (
    AboutUsImageSerializer,
    AboutUsListSerializer,
    AboutUsSerializer,
)
from apps.core.services import BaseService


class AboutUsService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = AboutUsRepository()

    def get_about_us(self, *args, **kwargs):
        about = self.db.get_about_us()
        return self.get_response_object(
            about,
            AboutUsListSerializer,
            context={"request": self.request},
        )

    def create_about_us(self, *args, **kwargs):
        serializer = AboutUsSerializer(
            instance=self.db.get_about_us(),
            data=self.request.data,
            context={"request": self.request},
        )
        serializer.is_valid(raise_exception=True)
        about = serializer.save()
        return self.get_response_object(
            about, AboutUsListSerializer, context={"request": self.request}
        )


class AboutUsImagesService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = AboutUsRepository()

    def create_about_us_image(self, *args, **kwargs):
        serializer = AboutUsImageSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        images = serializer.save()
        return self.get_response_object(
            images, AboutUsImageSerializer, context={"request": self.request}
        )
