from django.db import models

from products.models import Product
from materials.models import Material


class BOM(models.Model):
    """Bill of Materials for a Product. Only one BOM per product should be
    is_active=True at a time -- that's the version used for MRP."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='boms')
    version = models.CharField(max_length=20, default='v1')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"BOM {self.version} for {self.product.name}"


class BOMItem(models.Model):
    bom = models.ForeignKey(BOM, on_delete=models.CASCADE, related_name='items')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity_required = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('bom', 'material')

    def __str__(self):
        return f"{self.material.name} x {self.quantity_required}"
