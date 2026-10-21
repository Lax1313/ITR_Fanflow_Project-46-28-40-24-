"""
Aggregates real numbers from every app for the main dashboard's KPI cards,
Chart.js visualizations, and the Smart Insights panel (predicted demand +
low-stock alerts + reorder recommendations). Every value here comes from a
DB query -- nothing is a placeholder, and nothing is cached, so counts and
charts always reflect the current state of the database on every request.
"""
import json
from decimal import Decimal

from django.db.models import Sum, Count, F

from forecasting.models import DemandForecast
from inventory.models import Inventory
from inventory.services import calculate_available_stock
from logistics.models import Shipment
from orders.models import CustomerOrder
from procurement.models import PurchaseOrder
from procurement.services import generate_recommendations_for_all_materials
from risk_management.models import RiskAlert
from suppliers.models import Supplier


def get_kpis():
    total_orders = CustomerOrder.objects.count()

    latest_forecast_total = DemandForecast.objects.order_by('-forecast_date').first()
    predicted_demand = latest_forecast_total.predicted_quantity if latest_forecast_total else 0

    inventory_value = Decimal('0')
    critical_materials = 0
    for inv in Inventory.objects.select_related('material').all():
        inventory_value += inv.current_stock * inv.material.unit_cost
        if calculate_available_stock(inv) < inv.reorder_level:
            critical_materials += 1

    active_suppliers = Supplier.objects.filter(status=Supplier.Status.ACTIVE).count()
    pending_pos = PurchaseOrder.objects.exclude(
        status__in=[PurchaseOrder.Status.RECEIVED, PurchaseOrder.Status.CANCELLED]
    ).count()
    procurement_cost = PurchaseOrder.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    open_risks = RiskAlert.objects.filter(is_resolved=False).count()

    return {
        'total_orders': total_orders,
        'predicted_demand': predicted_demand,
        'inventory_value': round(inventory_value, 2),
        'critical_materials': critical_materials,
        'active_suppliers': active_suppliers,
        'pending_pos': pending_pos,
        'procurement_cost': round(procurement_cost, 2),
        'open_risks': open_risks,
    }


def get_chart_data():
    """Returns a dict of Chart.js-ready datasets, JSON-serialized."""

    # Demand forecast: last 12 forecasts by date
    forecasts = DemandForecast.objects.select_related('product').order_by('forecast_date')[:12]
    demand_forecast = {
        'labels': [f"{f.product.name} ({f.forecast_date})" for f in forecasts],
        'data': [float(f.predicted_quantity) for f in forecasts],
    }

    # Inventory status: available stock vs reorder level per material (top 10 by risk)
    inventory_rows = []
    for inv in Inventory.objects.select_related('material').all():
        inventory_rows.append({
            'name': inv.material.name,
            'available': float(calculate_available_stock(inv)),
            'reorder_level': float(inv.reorder_level),
        })
    inventory_rows.sort(key=lambda r: r['available'] - r['reorder_level'])
    inventory_rows = inventory_rows[:10]
    inventory_status = {
        'labels': [r['name'] for r in inventory_rows],
        'available': [r['available'] for r in inventory_rows],
        'reorder_level': [r['reorder_level'] for r in inventory_rows],
    }

    # Supplier performance: reliability vs quality
    suppliers = Supplier.objects.filter(status=Supplier.Status.ACTIVE)[:10]
    supplier_performance = {
        'labels': [s.name for s in suppliers],
        'quality': [float(s.quality_score) for s in suppliers],
        'reliability': [float(s.reliability_score) for s in suppliers],
    }

    # Procurement cost by supplier
    po_by_supplier = (
        PurchaseOrder.objects.values('supplier__name')
        .annotate(total=Sum('total_amount'))
        .order_by('-total')[:8]
    )
    procurement_cost = {
        'labels': [row['supplier__name'] for row in po_by_supplier],
        'data': [float(row['total'] or 0) for row in po_by_supplier],
    }

    # Material shortage
    shortage_rows = []
    for inv in Inventory.objects.select_related('material').all():
        available = calculate_available_stock(inv)
        if available < inv.reorder_level:
            shortage_rows.append({'name': inv.material.name, 'shortage': float(inv.reorder_level - available)})
    shortage_rows.sort(key=lambda r: -r['shortage'])
    material_shortage = {
        'labels': [r['name'] for r in shortage_rows[:10]],
        'data': [r['shortage'] for r in shortage_rows[:10]],
    }

    # Logistics status breakdown
    logistics_counts = Shipment.objects.values('status').annotate(count=Count('id'))
    logistics_status = {
        'labels': [row['status'].title() for row in logistics_counts],
        'data': [row['count'] for row in logistics_counts],
    }

    return {
        'demand_forecast': json.dumps(demand_forecast),
        'inventory_status': json.dumps(inventory_status),
        'supplier_performance': json.dumps(supplier_performance),
        'procurement_cost': json.dumps(procurement_cost),
        'material_shortage': json.dumps(material_shortage),
        'logistics_status': json.dumps(logistics_status),
    }


def get_smart_insights():
    """
    Powers the dashboard's Smart Insights panel:
      - predicted demand for each active product (from the trained ML model)
      - low-stock alerts (available stock below reorder level, right now)
      - reorder recommendations (from the same procurement service used on
        the Procurement page, so the numbers always match)
    """
    from products.models import Product

    predicted_demand = []
    for product in Product.objects.filter(is_active=True):
        latest = product.forecasts.order_by('-forecast_date').first()
        if latest:
            predicted_demand.append({
                'product': product,
                'predicted_quantity': latest.predicted_quantity,
                'forecast_date': latest.forecast_date,
                'model_name': latest.model_name,
                'confidence': latest.confidence_score,
            })

    low_stock = []
    for inv in Inventory.objects.select_related('material').all():
        available = calculate_available_stock(inv)
        if available < inv.reorder_level:
            low_stock.append({
                'material': inv.material,
                'available': available,
                'reorder_level': inv.reorder_level,
                'deficit': inv.reorder_level - available,
            })
    low_stock.sort(key=lambda r: -r['deficit'])

    reorder_recommendations = generate_recommendations_for_all_materials()

    return {
        'predicted_demand': predicted_demand[:6],
        'low_stock': low_stock[:8],
        'reorder_recommendations': reorder_recommendations[:6],
    }
