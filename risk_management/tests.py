from decimal import Decimal

from django.test import TestCase

from inventory.models import Inventory
from materials.models import Material
from .services import detect_inventory_risk
from .models import RiskAlert


class RiskEngineTests(TestCase):
    def test_detects_inventory_below_safety_stock(self):
        material = Material.objects.create(name='Understocked Material', unit='PCS', unit_cost=Decimal('5'))
        Inventory.objects.create(
            material=material, current_stock=10, reserved_stock=0, incoming_stock=0,
            reorder_level=100, safety_stock=50, maximum_stock=500,
        )
        created = detect_inventory_risk()
        self.assertEqual(len(created), 1)
        self.assertEqual(created[0].risk_type, RiskAlert.RiskType.INVENTORY)
        self.assertEqual(created[0].severity, RiskAlert.Severity.HIGH)
