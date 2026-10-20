from django.conf import settings
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
