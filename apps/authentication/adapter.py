from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        extra_data = sociallogin.account.extra_data or {}
        name = extra_data.get("name") or ""
        if not name:
            first_name = extra_data.get("given_name") or data.get("first_name") or ""
            last_name = extra_data.get("family_name") or data.get("last_name") or ""
            name = f"{first_name} {last_name}".strip()

        user.full_name = name or user.email.split("@")[0]

        if not hasattr(user, "phone_number") or not user.phone_number:
            user.phone_number = ""

        user.is_active = True
        user.is_verified = True

        return user
