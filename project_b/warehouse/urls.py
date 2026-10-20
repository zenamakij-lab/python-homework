from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InventorySyncAPIView, InventoryViewSet

router = DefaultRouter()
router.register(r"warehouse/inventory", InventoryViewSet, basename="inventory")

urlpatterns = [
    path("", include(router.urls)),
    path("warehouse/sync/", InventorySyncAPIView.as_view(), name="inventory-sync"),
]
