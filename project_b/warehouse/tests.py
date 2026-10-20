from django.test import TestCase
from rest_framework.test import APIClient

from .models import InventoryItem


class InventoryAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.inventory = InventoryItem.objects.create(
            sku="BK-100",
            product_name="Django for Beginners",
            available_quantity=12,
            reserved_quantity=0,
            location="A-01",
        )

    def test_inventory_list(self):
        response = self.client.get("/api/warehouse/inventory/")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data["results"]), 0)

    def test_inventory_sync_reserves_quantity(self):
        response = self.client.post(
            "/api/warehouse/sync/",
            {"sku": "BK-100", "quantity": 3, "action": "reserve", "order_id": "ORD-42"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.reserved_quantity, 3)
        self.assertEqual(self.inventory.available_quantity, 9)

    def test_inventory_sync_releases_quantity(self):
        self.inventory.reserved_quantity = 5
        self.inventory.available_quantity = 7
        self.inventory.save(update_fields=["reserved_quantity", "available_quantity"])

        response = self.client.post(
            "/api/warehouse/sync/",
            {"sku": "BK-100", "quantity": 2, "action": "release", "order_id": "ORD-43"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.reserved_quantity, 3)
        self.assertEqual(self.inventory.available_quantity, 9)
