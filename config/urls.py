# ============================================
# Root URL Configuration
# Central URL routing for the entire project.
# Includes API endpoints, admin, and Swagger documentation.
# ============================================

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),
    # API Endpoints (presentation layer)
    path("api/users/", include("apps.users.presentation.urls", namespace="users")),
    path("api/books/", include("apps.books.presentation.urls", namespace="books")),
    # API Schema & Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
