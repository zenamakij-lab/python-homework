import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import InventoryItem
from .serializers import InventoryItemSerializer, InventorySyncSerializer

logger = logging.getLogger("warehouse.api")


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class InventoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryItem.objects.all().order_by("sku")
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.AllowAny]


class InventorySyncAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = InventorySyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        sku = payload["sku"]
        quantity = payload["quantity"]
        action = payload["action"]
        order_id = payload.get("order_id", "")

        try:
            with transaction.atomic():
                item, _ = InventoryItem.objects.get_or_create(
                    sku=sku,
                    defaults={
                        "product_name": sku,
                        "available_quantity": 0,
                        "reserved_quantity": 0,
                        "location": "auto-sync",
                    },
                )
                if action == "reserve":
                    item.reserve(quantity)
                elif action == "release":
                    item.release(quantity)
                item.save(update_fields=["available_quantity", "reserved_quantity", "updated_at"])
        except ValidationError as exc:
            logger.warning("Inventory sync validation failed: %s", exc)
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            logger.exception("Inventory sync failed for sku=%s order_id=%s", sku, order_id)
            return Response({"error": "Inventory sync failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.info(
            "Inventory sync successful: sku=%s action=%s quantity=%s order_id=%s",
            sku,
            action,
            quantity,
            order_id,
        )
        return Response(
            {
                "status": "ok",
                "sku": sku,
                "action": action,
                "quantity": quantity,
                "order_id": order_id,
                "available_quantity": item.available_quantity,
                "reserved_quantity": item.reserved_quantity,
            },
            status=status.HTTP_200_OK,
        )
