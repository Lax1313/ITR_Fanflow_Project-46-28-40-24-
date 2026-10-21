"""
Generates a consistent, realistic demo dataset for the fan manufacturing
supply chain: products, materials, BOMs, suppliers, supplier-material
pricing, inventory, 3 years of sales history, customer orders, purchase
orders, and shipments.

Usage:
    python manage.py generate_demo_data
    python manage.py generate_demo_data --reset   # wipes existing demo data first
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from inventory.models import Inventory, InventoryTransaction
from logistics.models import Shipment
from materials.models import Material
from orders.models import CustomerOrder, SalesHistory
from procurement.models import PurchaseOrder, PurchaseOrderItem
from production.models import BOM, BOMItem
from products.models import Product
from suppliers.models import Supplier, SupplierMaterial

random.seed(42)

REGIONS = ['North', 'South', 'East', 'West']
CUSTOMERS = [
    'BrightHome Retailers', 'CoolAir Distributors', 'Metro Electricals',
    'Sunrise Hardware', 'Value Mart Wholesale', 'Prime Electronics',
    'Everest Trading Co', 'Coastal Appliances', 'Highland Supplies',
    'Urban Fan Bazaar', 'Greenfield Traders', 'National Electric Store',
]

PRODUCTS = [
    ('Aero Classic 48"', 'FAN-CL-48', 'Ceiling Fan', Decimal('1499.00'), 8000, '75W'),
    ('Aero Premium 48"', 'FAN-PR-48', 'Ceiling Fan', Decimal('2299.00'), 5000, '65W'),
    ('Breeze Table Mini', 'FAN-TB-12', 'Table Fan', Decimal('899.00'), 6000, '55W'),
    ('Turbo Pedestal 16"', 'FAN-PD-16', 'Pedestal Fan', Decimal('1799.00'), 4000, '70W'),
    ('CompactAir Exhaust 8"', 'FAN-EX-08', 'Exhaust Fan', Decimal('699.00'), 7000, '35W'),
    ('WallBreeze 12"', 'FAN-WB-12', 'Wall Fan', Decimal('1299.00'), 3500, '60W'),
]

MATERIALS = [
    # name, category, unit, unit_cost, reorder_level, safety_stock, maximum_stock
    ('Motor Assembly', 'ELECTRICAL', 'PCS', Decimal('420.00'), 3000, 1500, 12000),
    ('Blade Set (3 blades)', 'PLASTIC', 'SET', Decimal('95.00'), 4000, 2000, 15000),
    ('Capacitor 2.5uF', 'ELECTRICAL', 'PCS', Decimal('35.00'), 3000, 1500, 12000),
    ('Ball Bearing', 'MECHANICAL', 'PCS', Decimal('18.00'), 6000, 3000, 20000),
    ('Body Shell', 'PLASTIC', 'PCS', Decimal('150.00'), 3000, 1500, 10000),
    ('Packaging Box', 'PACKAGING', 'PCS', Decimal('22.00'), 4000, 2000, 15000),
    ('Copper Winding Wire', 'RAW_METAL', 'KG', Decimal('780.00'), 1500, 800, 5000),
    ('Speed Regulator', 'ELECTRICAL', 'PCS', Decimal('65.00'), 2500, 1200, 9000),
    ('Blade Nut', 'MECHANICAL', 'PCS', Decimal('4.00'), 5000, 2500, 18000),
    ('Down Rod', 'MECHANICAL', 'PCS', Decimal('55.00'), 2500, 1200, 9000),
    ('Canopy Set', 'MECHANICAL', 'SET', Decimal('40.00'), 2500, 1200, 9000),
    ('Remote Control Unit', 'ELECTRICAL', 'PCS', Decimal('180.00'), 1500, 700, 6000),
    ('Fan Guard (Wire Mesh)', 'RAW_METAL', 'PCS', Decimal('60.00'), 2000, 1000, 8000),
    ('Base Plate', 'MECHANICAL', 'PCS', Decimal('90.00'), 1800, 900, 7000),
    ('Power Cord 1.5m', 'ELECTRICAL', 'PCS', Decimal('28.00'), 4000, 2000, 15000),
    ('Carton Sticker Label', 'PACKAGING', 'PCS', Decimal('1.50'), 5000, 2500, 20000),
]

SUPPLIERS = [
    ('Precision Motors Pvt Ltd', 'Coimbatore', Decimal('92'), Decimal('90')),
    ('EastWind Components', 'Pune', Decimal('85'), Decimal('80')),
    ('MetroCast Industries', 'Ludhiana', Decimal('78'), Decimal('75')),
    ('BlueRiver Plastics', 'Chennai', Decimal('88'), Decimal('85')),
    ('National Wire Works', 'Rajkot', Decimal('80'), Decimal('72')),
    ('Sunrise Electricals', 'Ahmedabad', Decimal('90'), Decimal('88')),
    ('Coastal Packaging Co', 'Kochi', Decimal('70'), Decimal('65')),
    ('Alpine Bearings Ltd', 'Faridabad', Decimal('86'), Decimal('82')),
    ('Vantage Electronics', 'Bengaluru', Decimal('94'), Decimal('91')),
    ('Horizon Metal Traders', 'Jaipur', Decimal('72'), Decimal('68')),
    ('Zenith Auto Components', 'Nashik', Decimal('83'), Decimal('79')),
    ('Falcon Industrial Supplies', 'Hyderabad', Decimal('76'), Decimal('55')),  # deliberately weak
]


class Command(BaseCommand):
    help = 'Generates a consistent demo dataset for the fan manufacturing supply chain.'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Delete existing demo data before generating.')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting existing demo data...')
            Shipment.objects.all().delete()
            PurchaseOrderItem.objects.all().delete()
            PurchaseOrder.objects.all().delete()
            InventoryTransaction.objects.all().delete()
            Inventory.objects.all().delete()
            SalesHistory.objects.all().delete()
            CustomerOrder.objects.all().delete()
            BOMItem.objects.all().delete()
            BOM.objects.all().delete()
            SupplierMaterial.objects.all().delete()
            Supplier.objects.all().delete()
            Material.objects.all().delete()
            Product.objects.all().delete()

        products = self._create_products()
        materials = self._create_materials()
        self._create_boms(products, materials)
        suppliers = self._create_suppliers()
        self._create_supplier_materials(suppliers, materials)
        self._create_inventory(materials)
        self._create_sales_history(products)
        self._create_customer_orders(products)
        purchase_orders = self._create_purchase_orders(suppliers, materials)
        self._create_shipments(purchase_orders)

        self.stdout.write(self.style.SUCCESS(
            f"\nDemo data ready: {Product.objects.count()} products, "
            f"{Material.objects.count()} materials, {Supplier.objects.count()} suppliers, "
            f"{SalesHistory.objects.count()} sales history rows, "
            f"{CustomerOrder.objects.count()} customer orders, "
            f"{PurchaseOrder.objects.count()} purchase orders, "
            f"{Shipment.objects.count()} shipments."
        ))

    def _create_products(self):
        products = []
        for name, model_number, category, price, capacity, power in PRODUCTS:
            product, _ = Product.objects.update_or_create(
                model_number=model_number,
                defaults={
                    'name': name, 'category': category, 'selling_price': price,
                    'production_capacity': capacity, 'power_rating': power,
                    'description': f"{name} - {category} for residential and commercial use.",
                },
            )
            products.append(product)
        self.stdout.write(self.style.SUCCESS(f"Created/updated {len(products)} products."))
        return products

    def _create_materials(self):
        materials = []
        for name, category, unit, cost, reorder, safety, maximum in MATERIALS:
            material, _ = Material.objects.update_or_create(
                name=name,
                defaults={
                    'category': category, 'unit': unit, 'unit_cost': cost,
                    'reorder_level': reorder, 'safety_stock': safety, 'maximum_stock': maximum,
                },
            )
            materials.append(material)
        self.stdout.write(self.style.SUCCESS(f"Created/updated {len(materials)} materials."))
        return materials

    def _create_boms(self, products, materials):
        by_name = {m.name: m for m in materials}
        # Every fan shares a common core BOM, scaled slightly by product type.
        base_items = [
            ('Motor Assembly', Decimal('1')),
            ('Blade Set (3 blades)', Decimal('1')),
            ('Capacitor 2.5uF', Decimal('1')),
            ('Ball Bearing', Decimal('2')),
            ('Body Shell', Decimal('1')),
            ('Packaging Box', Decimal('1')),
            ('Copper Winding Wire', Decimal('0.4')),
            ('Power Cord 1.5m', Decimal('1')),
            ('Carton Sticker Label', Decimal('1')),
        ]
        extra_by_category = {
            'Ceiling Fan': [('Down Rod', Decimal('1')), ('Canopy Set', Decimal('1'))],
            'Pedestal Fan': [('Base Plate', Decimal('1')), ('Fan Guard (Wire Mesh)', Decimal('1'))],
            'Table Fan': [('Base Plate', Decimal('1')), ('Fan Guard (Wire Mesh)', Decimal('1'))],
            'Wall Fan': [('Fan Guard (Wire Mesh)', Decimal('1')), ('Speed Regulator', Decimal('1'))],
            'Exhaust Fan': [('Fan Guard (Wire Mesh)', Decimal('1'))],
        }

        count = 0
        for product in products:
            bom, _ = BOM.objects.update_or_create(
                product=product, version='v1', defaults={'is_active': True},
            )
            items = base_items + extra_by_category.get(product.category, [])
            if product.selling_price > Decimal('1800'):
                items = items + [('Remote Control Unit', Decimal('1'))]

            for material_name, qty in items:
                material = by_name.get(material_name)
                if material:
                    BOMItem.objects.update_or_create(bom=bom, material=material, defaults={'quantity_required': qty})
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Created/updated BOMs for {count} products."))

    def _create_suppliers(self):
        suppliers = []
        for name, location, quality, reliability in SUPPLIERS:
            supplier, _ = Supplier.objects.update_or_create(
                name=name,
                defaults={
                    'location': location, 'quality_score': quality, 'reliability_score': reliability,
                    'contact_person': f"{name.split()[0]} Sales Desk",
                    'email': f"sales@{name.lower().replace(' ', '').replace(chr(39), '')[:15]}.example.com",
                    'phone': f"+91-9{random.randint(100000000, 999999999)}",
                    'status': Supplier.Status.ACTIVE,
                },
            )
            suppliers.append(supplier)
        self.stdout.write(self.style.SUCCESS(f"Created/updated {len(suppliers)} suppliers."))
        return suppliers

    def _create_supplier_materials(self, suppliers, materials):
        count = 0
        for material in materials:
            chosen = random.sample(suppliers, k=random.randint(2, 4))
            for supplier in chosen:
                base_price = material.unit_cost
                price_variance = Decimal(str(round(random.uniform(0.85, 1.20), 2)))
                quality = Decimal(str(round(float(supplier.quality_score) + random.uniform(-8, 5), 1)))
                reliability = Decimal(str(round(float(supplier.reliability_score) + random.uniform(-8, 5), 1)))
                quality = max(Decimal('30'), min(Decimal('99'), quality))
                reliability = max(Decimal('30'), min(Decimal('99'), reliability))

                SupplierMaterial.objects.update_or_create(
                    supplier=supplier, material=material,
                    defaults={
                        'unit_price': (base_price * price_variance).quantize(Decimal('0.01')),
                        'lead_time_days': random.randint(3, 28),
                        'quality_score': quality,
                        'reliability_score': reliability,
                        'on_time_delivery_rate': Decimal(str(round(random.uniform(60, 99), 1))),
                        'minimum_order_quantity': random.choice([50, 100, 200, 500]),
                        'supplier_capacity': random.randint(2000, 20000),
                        'transportation_cost': Decimal(str(round(random.uniform(500, 5000), 2))),
                    },
                )
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Created/updated {count} supplier-material relationships."))

    def _create_inventory(self, materials):
        count = 0
        for i, material in enumerate(materials):
            # Deliberately understock every 4th material so risk/procurement
            # features have something real to detect and recommend on.
            understocked = (i % 4 == 0)
            current = int(material.reorder_level * (0.4 if understocked else random.uniform(1.1, 2.2)))
            Inventory.objects.update_or_create(
                material=material,
                defaults={
                    'current_stock': current,
                    'reserved_stock': int(current * random.uniform(0, 0.15)),
                    'incoming_stock': random.randint(0, int(material.reorder_level * 0.3)),
                    'reorder_level': material.reorder_level,
                    'safety_stock': material.safety_stock,
                    'maximum_stock': material.maximum_stock,
                },
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Created/updated inventory for {count} materials."))

    def _create_sales_history(self, products):
        SalesHistory.objects.all().delete()
        rows = []
        start_date = date.today().replace(day=1) - timedelta(days=3 * 365)
        month_cursor = start_date

        def season_for_month(m):
            if m in (3, 4, 5):
                return SalesHistory.Season.SUMMER
            if m in (6, 7, 8, 9):
                return SalesHistory.Season.MONSOON
            if m in (10, 11):
                return SalesHistory.Season.SPRING
            return SalesHistory.Season.WINTER

        months = []
        cursor = start_date
        today = date.today().replace(day=1)
        while cursor < today:
            months.append(cursor)
            year = cursor.year + (cursor.month // 12)
            month = cursor.month % 12 + 1
            cursor = date(year, month, 1)

        for product in products:
            base_demand = float(product.production_capacity) * 0.4
            for region in REGIONS:
                region_factor = {'North': 1.1, 'South': 0.9, 'East': 0.8, 'West': 1.2}[region]
                for m in months:
                    season = season_for_month(m.month)
                    seasonal_factor = {'SUMMER': 1.5, 'MONSOON': 0.7, 'WINTER': 0.6, 'SPRING': 1.0}[season]
                    festival = m.month in (10, 11)  # Diwali season
                    promotion = random.random() < 0.15
                    trend_factor = 1 + (m.year - start_date.year) * 0.05  # slow YoY growth

                    quantity = base_demand * region_factor * seasonal_factor * trend_factor
                    quantity *= 1.3 if festival else 1.0
                    quantity *= 1.2 if promotion else 1.0
                    quantity *= random.uniform(0.85, 1.15)

                    temperature = {
                        'SUMMER': random.uniform(32, 42), 'MONSOON': random.uniform(24, 30),
                        'WINTER': random.uniform(12, 22), 'SPRING': random.uniform(22, 30),
                    }[season]

                    rows.append(SalesHistory(
                        product=product, date=m, region=region,
                        quantity_sold=max(10, int(quantity)), temperature=round(temperature, 1),
                        season=season, festival_indicator=festival, promotion_indicator=promotion,
                    ))

        SalesHistory.objects.bulk_create(rows, batch_size=500)
        self.stdout.write(self.style.SUCCESS(f"Created {len(rows)} sales history rows."))

    def _create_customer_orders(self, products):
        CustomerOrder.objects.all().delete()
        statuses = list(CustomerOrder.Status.choices)
        priorities = list(CustomerOrder.Priority.choices)
        orders = []
        for _ in range(60):
            product = random.choice(products)
            order_date = date.today() - timedelta(days=random.randint(0, 90))
            orders.append(CustomerOrder(
                customer_name=random.choice(CUSTOMERS),
                product=product,
                quantity=random.randint(50, 2000),
                order_date=order_date,
                required_delivery_date=order_date + timedelta(days=random.randint(7, 45)),
                region=random.choice(REGIONS),
                priority=random.choice(priorities)[0],
                status=random.choice(statuses)[0],
            ))
        CustomerOrder.objects.bulk_create(orders)
        self.stdout.write(self.style.SUCCESS(f"Created {len(orders)} customer orders."))

    def _create_purchase_orders(self, suppliers, materials):
        PurchaseOrderItem.objects.all().delete()
        PurchaseOrder.objects.all().delete()
        purchase_orders = []
        for _ in range(15):
            supplier = random.choice(suppliers)
            order_date = date.today() - timedelta(days=random.randint(0, 60))
            status = random.choice([s[0] for s in PurchaseOrder.Status.choices])
            po = PurchaseOrder.objects.create(
                supplier=supplier, order_date=order_date,
                expected_delivery_date=order_date + timedelta(days=random.randint(5, 25)),
                status=status,
            )
            supplier_materials = list(SupplierMaterial.objects.filter(supplier=supplier))
            if not supplier_materials:
                continue
            for sm in random.sample(supplier_materials, k=min(len(supplier_materials), random.randint(1, 3))):
                qty = Decimal(random.randint(100, 3000))
                PurchaseOrderItem.objects.create(
                    purchase_order=po, material=sm.material, quantity=qty, unit_price=sm.unit_price,
                )
            po.recalculate_total()
            purchase_orders.append(po)
        self.stdout.write(self.style.SUCCESS(f"Created {len(purchase_orders)} purchase orders."))
        return purchase_orders

    def _create_shipments(self, purchase_orders):
        Shipment.objects.all().delete()
        count = 0
        for po in purchase_orders:
            total_qty = sum((item.quantity for item in po.items.all()), start=Decimal('0'))
            if total_qty <= 0:
                continue
            status_choices = [s[0] for s in Shipment.Status.choices]
            status = random.choice(status_choices)
            dispatch_date = po.order_date + timedelta(days=random.randint(1, 5))
            expected_arrival = po.expected_delivery_date
            # A couple of shipments deliberately overdue, for the risk engine to catch.
            if random.random() < 0.2:
                expected_arrival = date.today() - timedelta(days=random.randint(1, 10))
                status = Shipment.Status.IN_TRANSIT

            Shipment.objects.create(
                purchase_order=po, supplier=po.supplier,
                origin=po.supplier.location, destination='Fan Manufacturing Plant, Pune',
                transport_mode=random.choice([t[0] for t in Shipment.TransportMode.choices]),
                quantity=total_qty, dispatch_date=dispatch_date, expected_arrival=expected_arrival,
                actual_arrival=expected_arrival if status == Shipment.Status.DELIVERED else None,
                transportation_cost=Decimal(str(round(random.uniform(1000, 15000), 2))),
                status=status,
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Created {count} shipments."))
