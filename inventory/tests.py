from decimal import Decimal

from django.test import TestCase

from materials.models import Material
from .models import Inventory
from .services import calculate_available_stock, calculate_shortage, is_sufficient


class InventoryServiceTests(TestCase):
    def setUp(self):
        self.material = Material.objects.create(
            name='Test Motor', category='ELECTRICAL', unit='PCS',
            unit_cost=Decimal('100'), reorder_level=100, safety_stock=50, maximum_stock=1000,
        )
        self.inventory = Inventory.objects.create(
            material=self.material, current_stock=200, reserved_stock=50, incoming_stock=20,
            reorder_level=100, safety_stock=50, maximum_stock=1000,
        )

    def test_available_stock_formula(self):
        # Available = Current + Incoming - Reserved = 200 + 20 - 50 = 170
        self.assertEqual(calculate_available_stock(self.inventory), Decimal('170'))

    def test_shortage_when_sufficient(self):
        self.assertEqual(calculate_shortage(100, self.inventory), Decimal('0'))
        self.assertTrue(is_sufficient(100, self.inventory))

    def test_shortage_when_insufficient(self):
        # Required 300, available 170 -> shortage 130
        self.assertEqual(calculate_shortage(300, self.inventory), Decimal('130'))
        self.assertFalse(is_sufficient(300, self.inventory))
