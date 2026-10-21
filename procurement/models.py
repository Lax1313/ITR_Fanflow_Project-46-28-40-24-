from django.conf import settings
from django.db import models

from materials.models import Material
from suppliers.models import Supplier


class PurchaseOrder(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SENT = 'SENT', 'Sent'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        RECEIVED = 'RECEIVED', 'Received'
        CANCELLED = 'CANCELLED', 'Cancelled'

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    order_date = models.DateField()
    expected_delivery_date = models.DateField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-order_date']

    def recalculate_total(self):
        total = sum((item.total_price for item in self.items.all()), start=0)
        self.total_amount = total
        self.save(update_fields=['total_amount'])

    def __str__(self):
        return f"PO #{self.id} - {self.supplier.name}"


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.material.name} x {self.quantity}"
