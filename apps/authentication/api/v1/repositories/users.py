from django.db.models import Count, DecimalField, Max, Sum, Value
from django.db.models.functions import Coalesce

from apps.authentication.models import User
from apps.core.exceptions import ObjectNotFoundException


class UserRepository:
    def get_users(self):
        users = User.objects.annotate(
            orders_count=Count("orders"),
            total_spent=Coalesce(
                Sum("orders__budget"),
                Value(0),
                output_field=DecimalField(max_digits=20, decimal_places=2),
            ),
            last_order_at=Max("orders__created_at"),
        ).order_by("-created_at")
        return users

    def get_user(self, user_id):
        user = self.get_users().filter(id=user_id).first()
        if not user:
            raise ObjectNotFoundException(
                message="User not found", message_key="user_not_found"
            )
        return user
