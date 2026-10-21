"""
Procurement recommendation service.

Considers: required quantity, current inventory, incoming stock, safety
stock, supplier MOQ, supplier capacity, supplier price, lead time,
reliability, transportation cost, and required date -- all from the
database, via the inventory and supplier services already built.
"""
from datetime import timedelta
from decimal import Decimal

from inventory.models import Inventory
from inventory.services import calculate_available_stock, calculate_shortage
from suppliers.services import recommended_supplier_for_material


def generate_procurement_recommendation(material, required_quantity=None, required_date=None):
    """
    Returns a dict describing the recommendation, or None if there's no
    shortage and nothing needs to be procured.

    {
        'material': Material,
        'recommended_supplier': Supplier,
        'recommended_quantity': Decimal,
        'estimated_cost': Decimal,
        'expected_delivery': date,
        'reason': str,
        'risk_level': 'Low' | 'Medium' | 'High',
    }
    """
    inventory, _ = Inventory.objects.get_or_create(material=material)
    available = calculate_available_stock(inventory)

    # If no explicit requirement was given, treat the reorder level as the
    # trigger quantity (i.e. "how much would keep us above reorder level").
    target_quantity = required_quantity if required_quantity is not None else inventory.reorder_level

    shortage = calculate_shortage(target_quantity, inventory)
    below_safety = available < inventory.safety_stock

    if shortage <= 0 and not below_safety:
        return None

    # Purchase enough to cover the shortage AND get back above safety stock.
    quantity_to_purchase = max(shortage, inventory.safety_stock - available, Decimal('0'))
    if quantity_to_purchase <= 0:
        return None

    best = recommended_supplier_for_material(material, required_quantity=quantity_to_purchase)
    if not best:
        # No supplier can meet the full quantity -- fall back to the
        # top-ranked supplier regardless of capacity/MOQ, and flag it.
        best = recommended_supplier_for_material(material)
        if not best:
            return {
                'material': material,
                'recommended_supplier': None,
                'recommended_quantity': quantity_to_purchase,
                'estimated_cost': None,
                'expected_delivery': None,
                'reason': 'No supplier is registered for this material.',
                'risk_level': 'High',
            }

    sm = best['supplier_material']
    quantity_to_purchase = max(quantity_to_purchase, sm.minimum_order_quantity)
    estimated_cost = (sm.unit_price * quantity_to_purchase) + sm.transportation_cost
    expected_delivery = timedelta(days=sm.lead_time_days)

    reasons = [
        f"{best['supplier'].name} has the highest overall supplier score "
        f"({best['overall_score']}/100) among suppliers who can meet the required quantity."
    ]
    if required_date:
        latest_safe_order_date = required_date - expected_delivery
        reasons.append(f"Order by {latest_safe_order_date} to arrive before {required_date}.")

    # Simple risk heuristic based on lead time and reliability.
    if sm.lead_time_days > 21 or sm.reliability_score < 60:
        risk_level = 'High'
    elif sm.lead_time_days > 10 or sm.reliability_score < 80:
        risk_level = 'Medium'
    else:
        risk_level = 'Low'

    return {
        'material': material,
        'recommended_supplier': best['supplier'],
        'supplier_material': sm,
        'recommended_quantity': quantity_to_purchase,
        'estimated_cost': estimated_cost,
        'expected_delivery_days': sm.lead_time_days,
        'reason': ' '.join(reasons),
        'risk_level': risk_level,
        'overall_score': best['overall_score'],
    }


def generate_recommendations_for_all_materials():
    """Runs generate_procurement_recommendation for every material that
    currently has an Inventory row, returning only the ones that need
    action."""
    from materials.models import Material

    recommendations = []
    for material in Material.objects.filter(is_active=True):
        rec = generate_procurement_recommendation(material)
        if rec:
            recommendations.append(rec)
    return recommendations
