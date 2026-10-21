from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import section_required

from .models import Inventory
from .services import calculate_available_stock, record_transaction


@section_required('inventory')
def inventory_list(request):
    rows = []
    for inv in Inventory.objects.select_related('material').all():
        available = calculate_available_stock(inv)
        rows.append({'inventory': inv, 'available': available, 'short': available < inv.reorder_level})
    return render(request, 'inventory/inventory_list.html', {'rows': rows})


@section_required('inventory')
def inventory_detail(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)

    if request.method == 'POST':
        transaction_type = request.POST.get('transaction_type')
        quantity = request.POST.get('quantity')
        notes = request.POST.get('notes', '')
        try:
            record_transaction(inventory.material, transaction_type, quantity, notes=notes)
            messages.success(request, "Transaction recorded.")
        except Exception as exc:
            messages.error(request, f"Could not record transaction: {exc}")
        return redirect('inventory:detail', pk=pk)

    transactions = inventory.material.transactions.all()[:20]
    return render(request, 'inventory/inventory_detail.html', {
        'inventory': inventory,
        'available': calculate_available_stock(inventory),
        'transactions': transactions,
    })
