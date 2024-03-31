from rest_framework.permissions import BasePermission as DrfBasePermission, SAFE_METHODS
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.permissions import BasePermission as DrfBasePermission

class BasePermission(DjangoModelPermissions):
    permission_group = ""

    perms_map = {
        "GET": ["%(permission_group)s:get"],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(permission_group)s:create"],
        "PUT": ["%(permission_group)s:update"],
        "PATCH": ["%(permission_group)s:update"],
        "DELETE": ["%(permission_group)s:delete"],
    }

    def get_required_permissions(self, method, model_cls=None):
        kwargs = {"permission_group": self.permission_group}
        return [perm % kwargs for perm in self.perms_map[method]]

    def has_permission(self, request, view):
        perms = self.get_required_permissions(request.method)
        return request.user.has_perms(perms)


class HasRolePerm(BasePermission):
    permission_group = "Role"


class CanManageAppPermission(BasePermission):
    permission_group = "App Permission"


class HasUserPerm(BasePermission):
    permission_group = "User"


class CanManageDistrictAdmin(BasePermission):
    permission_group = "District Admin"


class CanManageDivisionAdmin(BasePermission):
    permission_group = "Divisional admin"


class CanManageNationalAdmin(BasePermission):
    permission_group = "National admin"


class CurrentUserOrAdmin(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_staff or obj.pk == user.pk


class CanViewDistrictAuthorities(DrfBasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.has_perm("District authority:get")


class CanViewNationalAuthorities(DrfBasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.has_perm("National authority:get")


class CanViewDivisionalAuthorities(DrfBasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.has_perm("Divisional authority:get")