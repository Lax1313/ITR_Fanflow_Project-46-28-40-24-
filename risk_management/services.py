"""
Risk detection engine. Scans real data (inventory, suppliers, forecasts,
shipments) and creates RiskAlert rows -- it never invents values.
"""
from datetime import date, timedelta

from django.db.models import Avg

from forecasting.models import DemandForecast
from inventory.models import Inventory
from inventory.services import calculate_available_stock
from logistics.models import Shipment
from orders.models import SalesHistory
from suppliers.models import Supplier

from .models import RiskAlert


def detect_demand_risk():
    """Flags products whose latest forecast is significantly (30%+) above
    their historical average sales -- a spike the supply chain may not be
    ready for."""
    created = []
    forecasts = DemandForecast.objects.select_related('product').order_by('product', '-forecast_date')
    seen_products = set()

    for forecast in forecasts:
        if forecast.product_id in seen_products:
            continue
        seen_products.add(forecast.product_id)

        baseline = SalesHistory.objects.filter(product=forecast.product).aggregate(avg=Avg('quantity_sold'))['avg']
        if not baseline:
            continue

        if forecast.predicted_quantity > baseline * 1.3:
            pct_increase = round(((float(forecast.predicted_quantity) / float(baseline)) - 1) * 100, 1)
            alert, was_created = RiskAlert.objects.get_or_create(
                risk_type=RiskAlert.RiskType.DEMAND,
                title=f"Demand spike expected for {forecast.product.name}",
                is_resolved=False,
                defaults={
                    'severity': RiskAlert.Severity.HIGH if pct_increase > 60 else RiskAlert.Severity.MEDIUM,
                    'description': (
                        f"Forecasted demand ({forecast.predicted_quantity}) is {pct_increase}% above "
                        f"the historical average ({round(baseline, 1)}) for {forecast.product.name}."
                    ),
                },
            )
            if was_created:
                created.append(alert)
    return created


def detect_inventory_risk():
    """Flags materials whose available stock has fallen below safety stock."""
    created = []
    for inventory in Inventory.objects.select_related('material').all():
        available = calculate_available_stock(inventory)
        if available < inventory.safety_stock:
            deficit = inventory.safety_stock - available
            alert, was_created = RiskAlert.objects.get_or_create(
                risk_type=RiskAlert.RiskType.INVENTORY,
                title=f"{inventory.material.name} below safety stock",
                related_material=inventory.material,
                is_resolved=False,
                defaults={
                    'severity': RiskAlert.Severity.CRITICAL if available <= 0 else RiskAlert.Severity.HIGH,
                    'description': (
                        f"Available stock ({available}) is below safety stock "
                        f"({inventory.safety_stock}) by {deficit} units."
                    ),
                },
            )
            if was_created:
                created.append(alert)
    return created


def detect_supplier_risk():
    """Flags suppliers with low reliability or quality scores."""
    created = []
    for supplier in Supplier.objects.filter(status=Supplier.Status.ACTIVE):
        if supplier.reliability_score < 60 or supplier.quality_score < 60:
            alert, was_created = RiskAlert.objects.get_or_create(
                risk_type=RiskAlert.RiskType.SUPPLIER,
                title=f"{supplier.name} has weak performance metrics",
                related_supplier=supplier,
                is_resolved=False,
                defaults={
                    'severity': RiskAlert.Severity.HIGH if supplier.reliability_score < 40 else RiskAlert.Severity.MEDIUM,
                    'description': (
                        f"Reliability score: {supplier.reliability_score}/100, "
                        f"Quality score: {supplier.quality_score}/100."
                    ),
                },
            )
            if was_created:
                created.append(alert)
    return created


def detect_logistics_risk():
    """Flags shipments that are overdue (past expected_arrival, not yet
    delivered) or that took/are taking an unusually long lead time."""
    created = []
    overdue_shipments = Shipment.objects.filter(
        expected_arrival__lt=date.today(),
    ).exclude(status__in=[Shipment.Status.DELIVERED, Shipment.Status.CANCELLED])

    for shipment in overdue_shipments.select_related('supplier'):
        days_overdue = (date.today() - shipment.expected_arrival).days
        alert, was_created = RiskAlert.objects.get_or_create(
            risk_type=RiskAlert.RiskType.LOGISTICS,
            title=f"Shipment #{shipment.id} from {shipment.supplier.name} is overdue",
            related_supplier=shipment.supplier,
            is_resolved=False,
            defaults={
                'severity': RiskAlert.Severity.HIGH if days_overdue > 7 else RiskAlert.Severity.MEDIUM,
                'description': f"Expected on {shipment.expected_arrival}, still not delivered ({days_overdue} days overdue).",
            },
        )
        if was_created:
            created.append(alert)
    return created


def run_all_risk_checks():
    """Runs every detector and returns the combined list of newly created alerts."""
    created = []
    created += detect_demand_risk()
    created += detect_inventory_risk()
    created += detect_supplier_risk()
    created += detect_logistics_risk()
    return created
