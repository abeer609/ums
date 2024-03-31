from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import SAFE_METHODS
from users.permissions import HasRolePerm, CanManageAppPermission, HasUserPerm, CanManageDistrictAdmin, \
    CanManageDivisionAdmin, CanManageNationalAdmin, CanViewDistrictAuthorities, CanViewDivisionalAuthorities, \
    CanViewNationalAuthorities
from .models import (
    AppPermissionGroup,
    Role,
    User,
)
from .serializers import (
    PermissionGroupSerializer,
    CreateUserSerializer,
    RoleSerializer,
    UserSerializer,
)
from .utils import UserConfirmationEmail

from django.db.models import Q


class MyPagination(PageNumberPagination):
    page_size = 50


class RegistrationView(CreateModelMixin, GenericViewSet):
    serializer_class = CreateUserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        print(user.username)
        UserConfirmationEmail(self.request, {'username': user.username, 'role': user.role}).send(to=[user.email])


class RoleView(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, HasRolePerm]


# class OrganizationView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
#     queryset = Organization.objects.all()
#     serializer_class = OrganizationSerializer


class PermissionGroupViewSet(ModelViewSet):
    queryset = AppPermissionGroup.objects.all()
    serializer_class = PermissionGroupSerializer
    permission_classes = [IsAuthenticated, CanManageAppPermission]


class UserViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    pagination_class = MyPagination
    permission_classes = [IsAuthenticated, HasUserPerm]

    def get_queryset(self):
        user = self.request.user

        admin_access_map = {
            'National Admin': Q(role__label='Divisional Admin'),
            'Divisional Admin': Q(role__label='District Admin') & Q(division=user.division),
            'District Admin': 'Upazilla Admin',
        }

        user_role = user.role.label

        if "National" in user_role:
            query = Q(role__label=admin_access_map.get(user_role))
        else:
            query = admin_access_map.get(user_role)
        if user.is_superuser:
            return User.objects.all()
        return User.objects.filter(query)

    @action(detail=False, methods=["get", "put", "patch"])
    def me(self, request, *args, **kwargs):
        self.get_object = lambda: self.request.user

        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "PUT":
            return self.update(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)


class AdminViewSet(ModelViewSet):
    pagination_class = MyPagination

    def get_serializer_class(self):
        if self.request.method not in SAFE_METHODS:
            return CreateUserSerializer
        return UserSerializer


class AuthorityViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    pagination_class = MyPagination
    serializer_class = UserSerializer


class DivisionAdminViewSet(AdminViewSet):
    queryset = User.objects.filter(role__label='Divisional Admin')
    permission_classes = [IsAuthenticated, CanManageDivisionAdmin]


class DistrictAdminViewSet(AdminViewSet):
    queryset = User.objects.filter(role__label='District Admin')
    permission_classes = [IsAuthenticated, CanManageDistrictAdmin]


class NationalAdminViewSet(AdminViewSet):
    queryset = User.objects.filter(role__label='National Admin')
    permission_classes = [IsAuthenticated, CanManageNationalAdmin]


class NationalAuthorityViewSet(AuthorityViewSet):
    queryset = User.objects.filter(role__label='National Authority')
    permission_classes = [IsAuthenticated, CanViewNationalAuthorities]


class DistrictAuthorityViewSet(AuthorityViewSet):
    queryset = User.objects.filter(role__label='District Authority')
    permission_classes = [IsAuthenticated, CanViewDistrictAuthorities]


class DivisionAuthorityViewSet(AuthorityViewSet):
    queryset = User.objects.filter(role__label='Divisional Authority')
    permission_classes = [IsAuthenticated, CanViewDivisionalAuthorities]
