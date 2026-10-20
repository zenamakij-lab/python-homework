from django.core.exceptions import ValidationError
from django.db import models


class InventoryItem(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    product_name = models.CharField(max_length=255)
    available_quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=100, default="unknown")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("sku",)

    def reserve(self, quantity):
        if quantity > self.available_quantity:
            raise ValidationError(
                f"Not enough available stock for SKU {self.sku}. "
                f"Requested {quantity}, available {self.available_quantity}."
            )
        self.available_quantity -= quantity
        self.reserved_quantity += quantity

    def release(self, quantity):
        if quantity > self.reserved_quantity:
            raise ValidationError(
                f"Cannot release {quantity} units for SKU {self.sku}; "
                f"only {self.reserved_quantity} are reserved."
            )
        self.reserved_quantity -= quantity
        self.available_quantity += quantity

    def __str__(self):
        return f"{self.sku} - {self.product_name}"
