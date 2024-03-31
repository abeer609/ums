from django.contrib.auth.backends import ModelBackend
from django.db.models.base import Model


class CustomBackend(ModelBackend):

    def get_all_permissions(self, user_obj, obj):
        permissions = super().get_all_permissions(user_obj, obj)
        app_permissions = user_obj.role.permissions.all()
        for perm in app_permissions:
            permissions.add(perm.permission.code_name)
        print(permissions)
        return permissions
