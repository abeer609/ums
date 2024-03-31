from rest_framework import serializers
from django.db import transaction, IntegrityError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import AppPermission, AppPermissionGroup, Role, User

role_username_map = {
    'National Admin': 'nationaladmin',
    'National Authority': 'nationalauthority',
    'Divisional Authority': 'diveo',
    'Divisional Admin': 'divadmin',
    'District Authority': 'deo',
    'District Admin': 'disadmin'
}


# role_region_map = {
#     'Divisional Authority': '%(divison)s',
#     'Divisional Admin': 'divadmin',
#     'District Authority': 'diseo',
#     'District Admin': 'disadmin'
# }

# def generate_username(role):
#     i
#     kwargs = {
#         "division": "dhaka",
#         "city": "tangail"
#     }


class UserCreateMixin:
    def perform_create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data, is_active=False)
        return user

    def create(self, validated_data):
        role = validated_data.get('role')
        role_label = role.label
        if role_label == 'Divisional Authority':
            validated_data['username'] = f"{role_username_map.get(role_label)}@{validated_data.get('division').lower()}"
        elif role_label == 'Divisional Admin':
            validated_data['username'] = f"{role_username_map.get(role_label)}@{validated_data.get('division').lower()}"
        elif role_label == 'District Authority':
            validated_data['username'] = f"{role_username_map.get(role_label)}@{validated_data.get('city').lower()}"
        elif role_label == 'District Admin':
            validated_data['username'] = f"{role_username_map.get(role_label)}@{validated_data.get('city').lower()}"
        elif role_label == 'National Admin':
            validated_data['username'] = f"{role_username_map.get(role_label)}@clms"
        elif role_label == 'National Authority':
            validated_data['username'] = f"{role_username_map.get(role_label)}@clms"
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError({"detail": "user already exists"})
        return user


class CreateUserSerializer(UserCreateMixin, serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "password", "street", "post_office", "division",
                  "city", "post_code", "phone", "designation", "first_name", "last_name",
                  "department"]


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppPermission
        fields = ["id", "name", "code_name"]


class PermissionGroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = AppPermissionGroup
        fields = ["id", "group_name", "permissions"]


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ["id", "label", "key", "permissions"]

    def create(self, validated_data):
        perm_ids = self.initial_data.get("permissions", [])
        app_permission = AppPermission.objects.filter(pk__in=perm_ids)
        role = Role.objects.create(**validated_data)
        role.permissions.set(app_permission)
        return role

    def update(self, instance, validated_data):
        perm_ids = self.initial_data.get("permissions", [])
        instance.label = validated_data.get("label")
        instance.key = validated_data.get("key")
        app_permission = AppPermission.objects.filter(pk__in=perm_ids)
        instance.permissions.set(app_permission)
        instance.save()
        return instance


class SimpleRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ["id", "label", "key"]


class UserSerializer(serializers.ModelSerializer):
    # role = serializers.StringRelatedField(read_only=True)
    username = serializers.CharField(read_only=True)
    role = SimpleRoleSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "street", "post_office", "division",
                  "city", "post_code", "phone", "designation", "first_name", "last_name",
                  "department", "is_active"]


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["permissions"] = [perm.code_name for perm in user.role.permissions.all()]

        return token

#
# diveo eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzExNzQyNTQzLCJpYXQiOjE3MTE2NTYxNDMsImp0aSI6Ijk3MjQxMThjNWQ3ODRkZGZhNjZhZTU4N2Y4ZDM0ZjY4IiwidXNlcl9pZCI6ODUsInBlcm1pc3Npb25zIjpbIkRpc3RyaWN0IEFkbWluOmdldCJdfQ.zNBGbhh6JNzWgk014Vop_Dx7CzSdwDDwq58xTe01pEQ
# deo eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzExNzQyNTc1LCJpYXQiOjE3MTE2NTYxNzUsImp0aSI6ImE1ZmUwMzQ4M2I4MDRlZWZiZDFlMmJlNDg3NTdiOWE2IiwidXNlcl9pZCI6ODMsInBlcm1pc3Npb25zIjpbXX0.JK5llanhdQvwWzRTH2ld4JZmZgmpyAq-8CQdD946qjc
# national authority eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzExNzQyNTk4LCJpYXQiOjE3MTE2NTYxOTgsImp0aSI6IjJjMzE2MGRhMmYzYTRlODViY2JlNzQ3NmRiY2U0YmJhIiwidXNlcl9pZCI6ODEsInBlcm1pc3Npb25zIjpbIkRpdmlzaW9uYWwgYXV0aG9yaXR5OmdldCIsIkRpc3RyaWN0IGF1dGhvcml0eTpnZXQiXX0.xD9YpG-RtoiXVbHUf8OZnZoXf2heXSonYGYGvsVxxFQ
# national admin eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzExNzQyNjIyLCJpYXQiOjE3MTE2NTYyMjIsImp0aSI6ImE0ODk2Mzg4MzA1YTQ4OTA5ZTc5ZTNiZDkzNjJmZWY3IiwidXNlcl9pZCI6NzcsInBlcm1pc3Npb25zIjpbIkRpdmlzaW9uYWwgYWRtaW46Y3JlYXRlIiwiRGl2aXNpb25hbCBhZG1pbjp1cGRhdGUiLCJEaXZpc2lvbmFsIGFkbWluOmRlbGV0ZSIsIkRpdmlzaW9uYWwgYWRtaW46Z2V0IiwiRGl2aXNpb25hbCBhdXRob3JpdHk6Y3JlYXRlIiwiRGl2aXNpb25hbCBhdXRob3JpdHk6dXBkYXRlIiwiRGl2aXNpb25hbCBhdXRob3JpdHk6ZGVsZXRlIiwiRGl2aXNpb25hbCBhdXRob3JpdHk6Z2V0Il19.k90_FEe5jqxnlg5yIAsPrVAxJoBWBmRU0iqzRTGlW_U
