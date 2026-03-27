# ============================================
# Book URL Configuration (Presentation Layer)
# Uses DefaultRouter to auto-generate CRUD endpoints for BookViewSet.
# ============================================

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BookViewSet

app_name = "books"

# Router auto-generates: list, create, retrieve, update, partial_update, destroy
router = DefaultRouter()
router.register("", BookViewSet, basename="book")

urlpatterns = [
    path("", include(router.urls)),
]
