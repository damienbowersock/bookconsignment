from rest_framework import permissions


class IsAuthor(permissions.BasePermission):
    """
    Permission check for author users.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, "author_profile")
        )


class IsStaff(permissions.BasePermission):
    """
    Permission check for staff users (booksellers).
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, "staff_profile")
        )


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Permission check for object owners or staff users.
    """
    def has_object_permission(self, request, view, obj):
        # Staff can access their organization's objects
        if hasattr(request.user, "staff_profile"):
            if hasattr(obj, "org"):
                return obj.org == request.user.staff_profile.org
            return True

        # Authors can access their own objects
        if hasattr(request.user, "author_profile"):
            if hasattr(obj, "author"):
                return obj.author == request.user.author_profile
            if hasattr(obj, "user"):
                return obj.user == request.user
            return False

        return False


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Staff can perform any action, others can only read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return (
            request.user.is_authenticated and
            hasattr(request.user, "staff_profile")
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object owner can edit, others can only read.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check ownership
        if hasattr(obj, "author"):
            return (
                hasattr(request.user, "author_profile") and
                obj.author == request.user.author_profile
            )
        if hasattr(obj, "user"):
            return obj.user == request.user

        return False


class CanManageOrganization(permissions.BasePermission):
    """
    Permission for organization management (owners and managers only).
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if not hasattr(request.user, "staff_profile"):
            return False

        return request.user.staff_profile.role in ["owner", "manager"]


class CanManagePayouts(permissions.BasePermission):
    """
    Permission for payout management.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if not hasattr(request.user, "staff_profile"):
            return False

        # Only owners and managers can create/modify payouts
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.staff_profile.role in ["owner", "manager"]
