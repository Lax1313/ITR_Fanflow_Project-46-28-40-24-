from django.db import models

from procurement.models import PurchaseOrder
from suppliers.models import Supplier


class Shipment(models.Model):
    class TransportMode(models.TextChoices):
        ROAD = 'ROAD', 'Road'
        RAIL = 'RAIL', 'Rail'
        AIR = 'AIR', 'Air'
        SEA = 'SEA', 'Sea'

    class Status(models.TextChoices):
        PLANNED = 'PLANNED', 'Planned'
        DISPATCHED = 'DISPATCHED', 'Dispatched'
        IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
        DELIVERED = 'DELIVERED', 'Delivered'
        DELAYED = 'DELAYED', 'Delayed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='shipments')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='shipments')
    origin = models.CharField(max_length=150)
    destination = models.CharField(max_length=150, default='Fan Manufacturing Plant')
    transport_mode = models.CharField(max_length=10, choices=TransportMode.choices, default=TransportMode.ROAD)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    dispatch_date = models.DateField(null=True, blank=True)
    expected_arrival = models.DateField()
    actual_arrival = models.DateField(null=True, blank=True)
    transportation_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PLANNED)

    class Meta:
        ordering = ['-expected_arrival']

    @property
    def is_delayed(self):
        from datetime import date
        if self.status in (self.Status.DELIVERED, self.Status.CANCELLED):
            return False
        return date.today() > self.expected_arrival

    def __str__(self):
        return f"Shipment #{self.id} - {self.supplier.name} - {self.status}"
