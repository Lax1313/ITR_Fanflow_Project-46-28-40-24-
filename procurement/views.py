from datetime import date, timedelta

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import section_required
from materials.models import Material

from .models import PurchaseOrder, PurchaseOrderItem
from .services import generate_procurement_recommendation, generate_recommendations_for_all_materials


@section_required('procurement')
def recommendations(request):
    recs = generate_recommendations_for_all_materials()
    return render(request, 'procurement/recommendations.html', {'recommendations': recs})


@section_required('procurement')
def create_po_from_recommendation(request, material_id):
    material = get_object_or_404(Material, pk=material_id)
    rec = generate_procurement_recommendation(material)
    if not rec or not rec.get('recommended_supplier'):
        messages.error(request, "No procurement recommendation available for this material right now.")
        return redirect('procurement:recommendations')

    po = PurchaseOrder.objects.create(
        supplier=rec['recommended_supplier'],
        order_date=date.today(),
        expected_delivery_date=date.today() + timedelta(days=rec['expected_delivery_days']),
        status=PurchaseOrder.Status.DRAFT,
        created_by=request.user,
    )
    PurchaseOrderItem.objects.create(
        purchase_order=po,
        material=material,
        quantity=rec['recommended_quantity'],
        unit_price=rec['supplier_material'].unit_price,
    )
    po.recalculate_total()
    messages.success(request, f"Purchase order #{po.id} created for {material.name}.")
    return redirect('procurement:po_detail', pk=po.pk)


@section_required('procurement')
def po_list(request):
    orders = PurchaseOrder.objects.select_related('supplier').all()
    return render(request, 'procurement/po_list.html', {'orders': orders})


@section_required('procurement')
def po_detail(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    return render(request, 'procurement/po_detail.html', {'po': po})


@section_required('procurement')
def po_update_status(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = {choice[0] for choice in PurchaseOrder.Status.choices}
        if new_status in valid_statuses:
            old_status = po.status
            po.status = new_status
            po.save(update_fields=['status'])

            # Receiving a PO is exactly "materials purchased -> stock increases".
            # Only fire the inventory increase once, the moment it flips to
            # RECEIVED (not on every re-save), so stock isn't double-counted.
            if new_status == PurchaseOrder.Status.RECEIVED and old_status != PurchaseOrder.Status.RECEIVED:
                from inventory.services import record_transaction
                for item in po.items.select_related('material').all():
                    record_transaction(
                        item.material, 'PURCHASE', item.quantity,
                        reference=f"PO #{po.id}",
                        notes=f"Received from {po.supplier.name}",
                    )
                messages.success(
                    request,
                    f"PO #{po.id} marked as received. Inventory increased for "
                    f"{po.items.count()} material(s)."
                )
            else:
                messages.success(request, f"PO #{po.id} status updated to {po.get_status_display()}.")
    return redirect('procurement:po_detail', pk=pk)
