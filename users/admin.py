from django.contrib import admin

from users.models import (
    Role,
    User,
    AppPermission,
    AppPermissionGroup,
)

admin.site.register(Role)
admin.site.register(AppPermission)
admin.site.register(AppPermissionGroup)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'role', 'city', 'division', 'is_active']
    list_editable = ['role', 'city', 'division', 'is_active']