from .views import (
    PermissionGroupViewSet,
    RegistrationView,
    RoleView,
    UserViewSet, DivisionAdminViewSet, DistrictAdminViewSet, NationalAdminViewSet, DivisionAuthorityViewSet,
    DistrictAuthorityViewSet, NationalAuthorityViewSet,
)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView


router = DefaultRouter()
router.register("roles", RoleView, basename="role")
router.register("users", UserViewSet, basename="user")
router.register("permissions", PermissionGroupViewSet, basename="permission")
router.register("division/admins", DivisionAdminViewSet, basename="divadmin")
router.register("district/admins", DistrictAdminViewSet, basename="disadmins")
router.register("national/admins", NationalAdminViewSet, basename="national-admin")
router.register("division/authorities", DivisionAuthorityViewSet, basename="division-authority")
router.register("district/authorities", DistrictAuthorityViewSet, basename="district-authority")
router.register("national/authorities", NationalAuthorityViewSet, basename="national-authority")

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/register/", RegistrationView.as_view({"post": "create"})),
    # path("api/permissions/", CreatePermissionView.as_view()),
    # path("api/permissions/", ListPermissions.as_view()),
    path("api/login/", TokenObtainPairView.as_view()),
]
