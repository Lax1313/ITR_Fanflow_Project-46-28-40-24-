"""
Supplier scoring service.

Weights (Section 25 of the spec):
  Price             30%
  Quality           25%
  Delivery          20%
  Reliability       15%
  Lead Time         10%

All raw metrics are normalized to a 0-1 scale across the competing
suppliers for the same material before the weighted score is computed, so
the "best" value in each category always scores 1.0 and the rest are
relative to it. This is not hard-coded to any particular supplier.
"""
from decimal import Decimal

from .models import SupplierMaterial

WEIGHTS = {
    'price': Decimal('0.30'),
    'quality': Decimal('0.25'),
    'delivery': Decimal('0.20'),
    'reliability': Decimal('0.15'),
    'lead_time': Decimal('0.10'),
}


def _normalize(value, best, worst, lower_is_better=False):
    """Returns a 0-1 normalized score. Guards against a zero-width range."""
    value, best, worst = Decimal(value), Decimal(best), Decimal(worst)
    if best == worst:
        return Decimal('1')
    if lower_is_better:
        return (worst - value) / (worst - best)
    return (value - worst) / (best - worst)


def calculate_supplier_scores_for_material(material):
    """
    Scores every SupplierMaterial offering a given Material, normalized
    against each other. Returns a list of dicts sorted by score descending
    (best supplier first).
    """
    offerings = list(SupplierMaterial.objects.filter(material=material).select_related('supplier'))
    if not offerings:
        return []

    prices = [o.unit_price for o in offerings]
    qualities = [o.quality_score for o in offerings]
    deliveries = [o.on_time_delivery_rate for o in offerings]
    reliabilities = [o.reliability_score for o in offerings]
    lead_times = [o.lead_time_days for o in offerings]

    results = []
    for o in offerings:
        price_score = _normalize(o.unit_price, min(prices), max(prices), lower_is_better=True)
        quality_score = _normalize(o.quality_score, max(qualities), min(qualities))
        delivery_score = _normalize(o.on_time_delivery_rate, max(deliveries), min(deliveries))
        reliability_score = _normalize(o.reliability_score, max(reliabilities), min(reliabilities))
        lead_time_score = _normalize(o.lead_time_days, min(lead_times), max(lead_times), lower_is_better=True)

        overall = (
            price_score * WEIGHTS['price']
            + quality_score * WEIGHTS['quality']
            + delivery_score * WEIGHTS['delivery']
            + reliability_score * WEIGHTS['reliability']
            + lead_time_score * WEIGHTS['lead_time']
        )

        results.append({
            'supplier_material': o,
            'supplier': o.supplier,
            'price_score': round(price_score, 3),
            'quality_score': round(quality_score, 3),
            'delivery_score': round(delivery_score, 3),
            'reliability_score': round(reliability_score, 3),
            'lead_time_score': round(lead_time_score, 3),
            'overall_score': round(overall * 100, 2),  # 0-100 scale for display
        })

    results.sort(key=lambda r: r['overall_score'], reverse=True)
    return results


def calculate_supplier_score(supplier_material: SupplierMaterial):
    """Score for a single SupplierMaterial, normalized against its peers
    for the same material."""
    all_scores = calculate_supplier_scores_for_material(supplier_material.material)
    for row in all_scores:
        if row['supplier_material'].id == supplier_material.id:
            return row
    return None


def recommended_supplier_for_material(material, required_quantity=None):
    """
    Returns the top-ranked supplier for a material, optionally filtered to
    only suppliers whose capacity and MOQ can actually satisfy the
    required quantity.
    """
    scores = calculate_supplier_scores_for_material(material)
    if required_quantity is not None:
        scores = [
            s for s in scores
            if s['supplier_material'].supplier_capacity >= required_quantity
            and s['supplier_material'].minimum_order_quantity <= required_quantity
        ]
    return scores[0] if scores else None
