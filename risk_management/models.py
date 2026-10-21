from django.db import models

from materials.models import Material
from suppliers.models import Supplier


class RiskAlert(models.Model):
    class RiskType(models.TextChoices):
        DEMAND = 'DEMAND', 'Demand Risk'
        INVENTORY = 'INVENTORY', 'Inventory Risk'
        SUPPLIER = 'SUPPLIER', 'Supplier Risk'
        LOGISTICS = 'LOGISTICS', 'Logistics Risk'

    class Severity(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'

    risk_type = models.CharField(max_length=15, choices=RiskType.choices)
    severity = models.CharField(max_length=10, choices=Severity.choices)
    title = models.CharField(max_length=200)
    description = models.TextField()
    related_material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True, related_name='risk_alerts')
    related_supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True, related_name='risk_alerts')
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.severity}] {self.title}"
