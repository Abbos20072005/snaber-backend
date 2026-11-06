import os
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageOps
from rest_framework.pagination import PageNumberPagination


class BackendPageNumberPagination(PageNumberPagination):
    page_size_query_param = "page_size"


def set_guest_session_cookie(response, session_key):
    """Bind the guest cart/favorites to the session cookie.

    The API is served from another host, so the cookie has to be sent on cross-site
    requests — the attributes are taken from the Django settings to keep them in sync.
    """
    response.set_cookie(
        settings.SESSION_COOKIE_NAME,
        session_key,
        max_age=settings.SESSION_COOKIE_AGE,
        httponly=True,
        path=settings.SESSION_COOKIE_PATH,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        secure=settings.SESSION_COOKIE_SECURE,
    )

    return response


MAX_IMAGE_SIDE = 1200


def optimize_image(field_file):
    """Shrink a picture to a web size, so pages do not load multi-megabyte originals.

    Pictures without transparency become JPEG, the rest stay PNG. Files that are not
    JPEG, PNG or WebP pictures (SVG, GIF), and pictures with nothing to gain, are left
    as they are.
    """
    try:
        image = Image.open(field_file)
    except OSError:
        return
    if image.format not in ("JPEG", "PNG", "WEBP"):
        return

    is_png = image.format == "PNG"
    is_large = max(image.size) > MAX_IMAGE_SIDE
    image = ImageOps.exif_transpose(image)
    image.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))
    rgba = image.convert("RGBA")
    has_alpha = rgba.getchannel("A").getextrema()[0] < 255
    if not is_large and (has_alpha or not is_png):
        return

    buffer = BytesIO()
    if has_alpha:
        rgba.save(buffer, "PNG", optimize=True)
    else:
        rgba.convert("RGB").save(buffer, "JPEG", quality=85, optimize=True)

    extension = "png" if has_alpha else "jpg"
    name = f"{os.path.splitext(os.path.basename(field_file.name))[0]}.{extension}"
    field_file.save(name, ContentFile(buffer.getvalue()), save=False)
