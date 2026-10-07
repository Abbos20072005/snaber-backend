import django_filters

from apps.authentication.models import User


class UserFilter(django_filters.FilterSet):
    role = django_filters.ChoiceFilter(choices=User.Roles.choices)

    class Meta:
        model = User
        fields = ("role",)
