from decimal import Decimal

from django.test import TestCase

from materials.models import Material
from .models import Supplier, SupplierMaterial
from .services import calculate_supplier_scores_for_material


class SupplierScoringTests(TestCase):
    def setUp(self):
        self.material = Material.objects.create(name='Test Material', unit='PCS', unit_cost=Decimal('10'))
        self.cheap_reliable = Supplier.objects.create(name='Cheap & Reliable', quality_score=90, reliability_score=95)
        self.expensive_slow = Supplier.objects.create(name='Expensive & Slow', quality_score=60, reliability_score=50)

        SupplierMaterial.objects.create(
            supplier=self.cheap_reliable, material=self.material,
            unit_price=Decimal('10'), lead_time_days=5, quality_score=90,
            reliability_score=95, on_time_delivery_rate=95, minimum_order_quantity=10,
            supplier_capacity=5000, transportation_cost=Decimal('100'),
        )
        SupplierMaterial.objects.create(
            supplier=self.expensive_slow, material=self.material,
            unit_price=Decimal('25'), lead_time_days=25, quality_score=60,
            reliability_score=50, on_time_delivery_rate=60, minimum_order_quantity=10,
            supplier_capacity=5000, transportation_cost=Decimal('500'),
        )

    def test_best_supplier_ranks_first(self):
        scores = calculate_supplier_scores_for_material(self.material)
        self.assertEqual(scores[0]['supplier'], self.cheap_reliable)
        self.assertGreater(scores[0]['overall_score'], scores[1]['overall_score'])
