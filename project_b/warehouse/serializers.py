from rest_framework import serializers

from .models import InventoryItem


class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = [
            "id",
            "sku",
            "product_name",
            "available_quantity",
            "reserved_quantity",
            "location",
            "updated_at",
        ]


class InventorySyncSerializer(serializers.Serializer):
    sku = serializers.CharField(max_length=50)
    quantity = serializers.IntegerField(min_value=1)
    action = serializers.ChoiceField(choices=["reserve", "release"])
    order_id = serializers.CharField(required=False, allow_blank=True, default="")
