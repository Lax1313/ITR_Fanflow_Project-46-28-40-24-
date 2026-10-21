from decimal import Decimal

from django.test import TestCase

from materials.models import Material
from products.models import Product
from .models import BOM, BOMItem
from .services import calculate_material_requirements


class MRPServiceTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name='Test Fan', model_number='TF-001', category='Ceiling Fan',
            selling_price=Decimal('1000'), production_capacity=5000,
        )
        self.motor = Material.objects.create(name='Motor', unit='PCS', unit_cost=Decimal('50'))
        self.blade = Material.objects.create(name='Blade', unit='PCS', unit_cost=Decimal('10'))

        bom = BOM.objects.create(product=self.product, version='v1', is_active=True)
        BOMItem.objects.create(bom=bom, material=self.motor, quantity_required=Decimal('1'))
        BOMItem.objects.create(bom=bom, material=self.blade, quantity_required=Decimal('3'))

    def test_material_requirement_formula(self):
        # Material Requirement = Production Quantity x BOM Quantity
        requirements = calculate_material_requirements(self.product, 1000)
        by_material = {r['material'].name: r['quantity_required'] for r in requirements}
        self.assertEqual(by_material['Motor'], Decimal('1000'))
        self.assertEqual(by_material['Blade'], Decimal('3000'))
