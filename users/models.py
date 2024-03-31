from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


# from django.contrib.auth.backends import ModelBackend

# ORG_TYPES = [
#     ("NATIONAL", "National"),
#     ("DIVISIONAL", "Divisional"),
#     ("DISTRICT", "District"),
#     ("THANA", "Thana"),
# ]


# class Address(models.Model):
#     street = models.CharField(max_length=250)
#     post_office = models.CharField(max_length=150)
#     city = models.CharField(max_length=50)
#     post_code = models.CharField(max_length=4)


class Role(models.Model):
    label = models.CharField(max_length=50)
    key = models.CharField(max_length=50)
    permissions = models.ManyToManyField("AppPermission", blank=True)

    def __str__(self):
        return self.label


class User(AbstractUser):
    email = models.EmailField(unique=True)
    groups = None
    user_permissions = None
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, blank=True, null=True)
    # address = models.ForeignKey(Address, on_delete=models.SET_NULL, blank=True, null=True)
    street = models.CharField(max_length=250, blank=True, null=True)
    post_office = models.CharField(max_length=150, blank=True, null=True)
    division = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    post_code = models.CharField(max_length=4, blank=True, null=True)
    phone = models.CharField(max_length=11)
    designation = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ('-date_joined',)

    def has_perm(self, perm, obj=None) -> bool:
        if self.is_active and self.is_superuser:
            return True
        if self.role is None:
            return False
        return perm in self.role.permissions.values_list("code_name", flat=True)

    def has_perms(self, perm_list, obj=None):
        return all(self.has_perm(perm) for perm in perm_list)

    # def get_user_permissions(self, obj):
    #     permissions = super().get_user_permissions(obj)
    #     app_permissions = self.role.permissions.all()
    #     for perm in app_permissions:
    #         permissions.add(perm.permission.code_name)
    #     return permissions

    # def get_all_permissions(self, obj):
    #     return {*self.get_user_permissions(obj), *self.get_group_permissions(obj)}


class AppPermission(models.Model):
    code_name = models.CharField(max_length=100)
    group = models.ForeignKey(
        "AppPermissionGroup",
        related_name="permissions",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.code_name


class AppPermissionGroup(models.Model):
    group_name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.group_name


# class Organization(models.Model):
#     name = models.CharField(max_length=150)
#     short_id = models.CharField(
#         unique=True, max_length=21, editable=False, default=nanoid.generate
#     )
#     short_code = models.CharField(max_length=10)
#     description = models.TextField(blank=True)
#     type = models.CharField(max_length=20, choices=ORG_TYPES)
#     owner = models.ForeignKey(User, on_delete=models.CASCADE)
#     capacity = models.PositiveIntegerField()

#     def __str__(self) -> str:
#         return self.name


# class OrganizationMembership(models.Model):
#     # role = models.ForeignKey(Role, on_delete=models.CASCADE)
#     organization = models.ForeignKey(
#         Organization, on_delete=models.CASCADE, related_name="members"
#     )
#     user = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name="organizations"
#     )

#     class Meta:
#         unique_together = ("user", "organization")


@receiver(post_save, sender=AppPermissionGroup)
def create_permission(sender, instance: AppPermissionGroup, created, **kwargs):
    if created:
        AppPermission.objects.create(
            code_name=f"{instance.group_name}:create",
            name=f"Create {instance.group_name}",
            group=instance,
        )
        AppPermission.objects.create(
            code_name=f"{instance.group_name}:update",
            name=f"Update {instance.group_name}",
            group=instance,
        )
        AppPermission.objects.create(
            code_name=f"{instance.group_name}:delete",
            name=f"Delete {instance.group_name}",
            group=instance,
        )
        AppPermission.objects.create(
            code_name=f"{instance.group_name}:get",
            name=f"View {instance.group_name}",
            group=instance,
        )
