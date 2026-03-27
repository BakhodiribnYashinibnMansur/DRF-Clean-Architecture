# ============================================
# User URL Configuration (Presentation Layer)
# Routes for authentication, registration, profile, and user CRUD.
# ============================================

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import ChangePasswordView, RegisterView, UserProfileView, UserViewSet

app_name = "users"

# Router for UserViewSet — generates list/detail/create/update/delete URLs
router = DefaultRouter()
router.register("", UserViewSet, basename="user")

urlpatterns = [
    # Authentication — JWT token endpoints
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Registration — public endpoint
    path("register/", RegisterView.as_view(), name="register"),
    # Profile — authenticated user's own profile
    path("profile/", UserProfileView.as_view(), name="profile"),
    # Change password — authenticated user
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    # User CRUD — admin + self management (router-generated URLs)
    path("manage/", include(router.urls)),
]
