from django.db import models

from materials.models import Material


class Inventory(models.Model):
    material = models.OneToOneField(Material, on_delete=models.CASCADE, related_name='inventory')
    current_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reserved_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    incoming_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_level = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    safety_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    maximum_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Inventory'
        ordering = ['material__name']

    @property
    def available_stock(self):
        return self.current_stock + self.incoming_stock - self.reserved_stock

    def __str__(self):
        return f"{self.material.name}: {self.current_stock} in stock"


class InventoryTransaction(models.Model):
    class TransactionType(models.TextChoices):
        PURCHASE = 'PURCHASE', 'Purchase'
        SALE = 'SALE', 'Sale'
        PRODUCTION = 'PRODUCTION', 'Production'
        ADJUSTMENT = 'ADJUSTMENT', 'Adjustment'
        RETURN = 'RETURN', 'Return'

    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.transaction_type} - {self.material.name} - {self.quantity}"
