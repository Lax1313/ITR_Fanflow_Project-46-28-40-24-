from django.db import models

from materials.models import Material


class Supplier(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        BLACKLISTED = 'BLACKLISTED', 'Blacklisted'

    name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=150, blank=True)
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="0-100")
    reliability_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="0-100")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SupplierMaterial(models.Model):
    """Allows multiple suppliers to provide the same material, each with
    their own pricing, lead time, and performance metrics."""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='materials_supplied')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='suppliers_available')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    lead_time_days = models.PositiveIntegerField()
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="0-100")
    reliability_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="0-100")
    on_time_delivery_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="0-100 (%)")
    minimum_order_quantity = models.PositiveIntegerField(default=1)
    supplier_capacity = models.PositiveIntegerField(help_text="Max units/month this supplier can provide")
    transportation_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('supplier', 'material')
        ordering = ['material__name', 'unit_price']

    def __str__(self):
        return f"{self.supplier.name} -> {self.material.name} @ {self.unit_price}"
