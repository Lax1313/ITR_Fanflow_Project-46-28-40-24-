from django.shortcuts import render

from accounts.decorators import section_required
from inventory.models import Inventory
from inventory.services import calculate_available_stock
from risk_management.models import RiskAlert


@section_required('dashboard')
def notifications_list(request):
    """Unified notification feed: open risk alerts + low-stock materials.
    Reuses RiskAlert (which already covers stock/supplier/demand/procurement
    signals via the risk engine) rather than duplicating a second model."""
    alerts = RiskAlert.objects.filter(is_resolved=False)[:20]

    low_stock = []
    for inv in Inventory.objects.select_related('material').all():
        available = calculate_available_stock(inv)
        if available < inv.reorder_level:
            low_stock.append({'material': inv.material, 'available': available, 'reorder_level': inv.reorder_level})

    return render(request, 'notifications/list.html', {'alerts': alerts, 'low_stock': low_stock})
