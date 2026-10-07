from django.utils.translation import gettext_lazy as _

from apps.authentication.models import User
from apps.company.models import Company, CompanyMember




def format_response_time(seconds: int) -> str:
    if seconds < 60:
        return _("Less than a minute")
    minutes = seconds // 60
    if minutes < 60:
        if minutes == 1:
            return _("1 min")
        return _("%(mins)s min") % {"mins": minutes}
    hours = minutes // 60
    if hours < 24:
        if hours == 1:
            return _("1 hour")
        return _("%(hours)s hours") % {"hours": hours}
    days = hours // 24
    if days == 1:
        return _("1 day")
    return _("%(days)s days") % {"days": days}
