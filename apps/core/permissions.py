from rest_framework.permissions import BasePermission

from apps.authentication.models import User


class IsBuyer(BasePermission):
    message = "Only buyers can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Roles.BUYER
        )


class IsSeller(BasePermission):
    message = "Only sellers can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Roles.SELLER
        )


class IsModerator(BasePermission):
    message = "Only moderators can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Roles.MODERATOR
        )


class IsAdmin(BasePermission):
    message = "Only admins can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Roles.ADMIN
        )


class IsSuperAdmin(BasePermission):
    message = "Only super admins can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Roles.SUPER_ADMIN
        )


class IsAdminOrSuperAdmin(BasePermission):
    message = "Only admins or super admins can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in [User.Roles.ADMIN, User.Roles.SUPER_ADMIN]
        )


class IsModeratorOrAdmin(BasePermission):
    message = "Only moderators or admins can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role
            in [
                User.Roles.MODERATOR,
                User.Roles.ADMIN,
                User.Roles.SUPER_ADMIN,
            ]
        )


class IsSellerOrBuyer(BasePermission):
    message = "Only sellers or buyers can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in [User.Roles.SELLER, User.Roles.BUYER]
        )


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in ("GET", "HEAD", "OPTIONS")


def _get_user_membership(user):
    from apps.company.models import CompanyMember

    return CompanyMember.objects.select_related("company").filter(user=user).first()


class IsCompanyMember(BasePermission):
    message = "You must be a member of a company to perform this action."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        membership = _get_user_membership(request.user)
        if not membership:
            return False

        request.company_member = membership
        request.company = membership.company
        return True


def HasCompanyPermission(permission_type):

    class _HasCompanyPermission(BasePermission):
        message = f"You do not have the '{permission_type}' permission in your company."

        def has_permission(self, request, view):
            if not (request.user and request.user.is_authenticated):
                return False

            # Reuse membership if already attached by IsCompanyMember
            membership = getattr(request, "company_member", None)
            if not membership:
                membership = _get_user_membership(request.user)
                if not membership:
                    return False
                request.company_member = membership
                request.company = membership.company

            return membership.has_permission(permission_type)

    # Give the class a meaningful name for debugging and Swagger
    _HasCompanyPermission.__name__ = f"HasCompanyPermission_{permission_type}"
    _HasCompanyPermission.__qualname__ = f"HasCompanyPermission_{permission_type}"
    return _HasCompanyPermission


# Convenience aliases — ready to use directly in permission_classes
CanManageProducts = HasCompanyPermission("manage_products")
CanManageSales = HasCompanyPermission("manage_sales")
CanManageCompanyInfo = HasCompanyPermission("manage_company_info")
CanManageMembers = HasCompanyPermission("manage_members")
