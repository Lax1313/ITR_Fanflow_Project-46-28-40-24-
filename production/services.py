"""
Material Requirement Planning (MRP) service.

Material Requirement = Production Quantity x BOM Quantity
"""
from decimal import Decimal

from .models import BOM


def get_active_bom(product):
    return BOM.objects.filter(product=product, is_active=True).order_by('-created_at').first()


def calculate_material_requirements(product, production_quantity):
    """
    Returns a list of dicts:
      [{'material': Material, 'quantity_required': Decimal}, ...]

    quantity_required = production_quantity * BOM's quantity_required per unit
    """
    bom = get_active_bom(product)
    if not bom:
        return []

    production_quantity = Decimal(production_quantity)
    requirements = []
    for item in bom.items.select_related('material').all():
        requirements.append({
            'material': item.material,
            'quantity_per_unit': item.quantity_required,
            'quantity_required': item.quantity_required * production_quantity,
        })
    return requirements


def calculate_requirements_for_products(product_quantities):
    """
    product_quantities: dict {product_id: quantity}
    Returns aggregated material requirements across multiple products, e.g.
    when several products are being produced in the same planning cycle.

    Returns: {material_id: {'material': Material, 'quantity_required': Decimal}}
    """
    from products.models import Product

    aggregated = {}
    for product_id, quantity in product_quantities.items():
        product = Product.objects.get(pk=product_id)
        for req in calculate_material_requirements(product, quantity):
            mat_id = req['material'].id
            if mat_id not in aggregated:
                aggregated[mat_id] = {'material': req['material'], 'quantity_required': Decimal('0')}
            aggregated[mat_id]['quantity_required'] += req['quantity_required']
    return aggregated
