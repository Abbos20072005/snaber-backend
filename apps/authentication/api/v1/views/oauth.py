import os

from allauth.socialaccount.providers.google.provider import GoogleProvider
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.permissions import AllowAny


class CustomGoogleOAuth2Adapter(GoogleOAuth2Adapter):
    def get_callback_url(self, request, app):
        return os.getenv("GOOGLE_OAUTH_CALLBACK_URL", "http://localhost:3000")


# Override GoogleProvider's default adapter to use our custom adapter
GoogleProvider.oauth2_adapter_class = CustomGoogleOAuth2Adapter


class GoogleLoginView(SocialLoginView):
    adapter_class = CustomGoogleOAuth2Adapter
    callback_url = os.getenv("GOOGLE_OAUTH_CALLBACK_URL", "http://localhost:3000")
    client_class = OAuth2Client
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        adapter = self.adapter_class(request)
        provider = adapter.get_provider()
        response = provider.redirect_from_request(request)
        return response

    def post(self, request, *args, **kwargs):
        data = (
            request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        )
        code = data.get("code")

        if code:
            from urllib.parse import unquote

            data["code"] = unquote(code)

        request._full_data = data

        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            from apps.core.exceptions import ValidationError

            # Extract the raw exception cause if it exists
            error_msg = "Invalid Google OAuth code or token"
            if hasattr(e, "__cause__") and e.__cause__:
                error_msg = f"OAuth Error: {str(e.__cause__)}"
            elif str(e):
                error_msg = f"OAuth Error: {str(e)}"

            raise ValidationError(
                message=error_msg,
                message_key="invalid_oauth_token",
            ) from e

    def get_response(self):
        response = super().get_response()
        if hasattr(self, "user") and self.user:
            needs_setup = not bool(self.user.country)
            if hasattr(response, "data") and isinstance(response.data, dict):
                response.data["needs_setup"] = needs_setup
        return response
