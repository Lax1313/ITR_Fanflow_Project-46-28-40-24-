from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import section_required
from inventory.models import Inventory
from inventory.services import calculate_available_stock, calculate_shortage

from .forms import BOMForm, BOMItemFormSet, CompleteProductionForm, MRPForm
from .models import BOM
from .services import calculate_material_requirements


@section_required('bom')
def bom_list(request):
    boms = BOM.objects.select_related('product').all()
    return render(request, 'production/bom_list.html', {'boms': boms})


@section_required('bom')
def bom_add(request):
    if request.method == 'POST':
        form = BOMForm(request.POST)
        if form.is_valid():
            bom = form.save(commit=False)
            bom.save()
            formset = BOMItemFormSet(request.POST, instance=bom)
            if formset.is_valid():
                formset.save()
                messages.success(request, f"BOM created for {bom.product.name}.")
                return redirect('production:bom_detail', pk=bom.pk)
            bom.delete()
        else:
            formset = BOMItemFormSet(request.POST)
    else:
        form = BOMForm()
        formset = BOMItemFormSet()
    return render(request, 'production/bom_form.html', {'form': form, 'formset': formset})


@section_required('bom')
def bom_detail(request, pk):
    bom = get_object_or_404(BOM, pk=pk)
    return render(request, 'production/bom_detail.html', {'bom': bom})


@section_required('bom')
def bom_edit(request, pk):
    bom = get_object_or_404(BOM, pk=pk)
    if request.method == 'POST':
        form = BOMForm(request.POST, instance=bom)
        formset = BOMItemFormSet(request.POST, instance=bom)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f"BOM for {bom.product.name} updated.")
            return redirect('production:bom_detail', pk=bom.pk)
    else:
        form = BOMForm(instance=bom)
        formset = BOMItemFormSet(instance=bom)
    return render(request, 'production/bom_form.html', {'form': form, 'formset': formset, 'mode': 'edit', 'bom': bom})


@section_required('bom')
def mrp_calculator(request):
    requirements = None
    if request.method == 'POST':
        form = MRPForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['production_quantity']
            requirements = calculate_material_requirements(product, quantity)
            for req in requirements:
                inv, _ = Inventory.objects.get_or_create(material=req['material'])
                req['available'] = calculate_available_stock(inv)
                req['shortage'] = calculate_shortage(req['quantity_required'], inv)
    else:
        form = MRPForm()
    return render(request, 'production/mrp_calculator.html', {'form': form, 'requirements': requirements})


@section_required('bom')
def complete_production(request):
    """
    "We just finished manufacturing 50 fans" -> automatically:
      1. Explode the BOM for that quantity (Material Requirement = Qty x BOM Qty)
      2. Deduct every required material from Inventory (a real InventoryTransaction
         of type PRODUCTION is recorded for each one -- full audit trail)
      3. Immediately re-run the inventory risk check so any material that just
         dropped below safety stock is flagged right away, with no extra steps.
    """
    result = None
    if request.method == 'POST':
        form = CompleteProductionForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity_produced']
            reference = form.cleaned_data['reference'] or f"Production run - {product.name}"

            requirements = calculate_material_requirements(product, quantity)
            if not requirements:
                messages.error(request, f"{product.name} has no active BOM yet -- nothing to deduct.")
                return redirect('production:complete_production')

            from inventory.services import record_transaction, calculate_available_stock
            from inventory.models import Inventory
            from risk_management.services import detect_inventory_risk

            deducted = []
            for req in requirements:
                record_transaction(
                    req['material'], 'PRODUCTION', req['quantity_required'],
                    reference=reference,
                    notes=f"Auto-deducted: {quantity} x {product.name} completed.",
                )
                inv = Inventory.objects.get(material=req['material'])
                deducted.append({
                    'material': req['material'],
                    'quantity_deducted': req['quantity_required'],
                    'remaining_available': calculate_available_stock(inv),
                    'reorder_level': inv.reorder_level,
                    'now_short': calculate_available_stock(inv) < inv.reorder_level,
                })

            new_alerts = detect_inventory_risk()

            messages.success(
                request,
                f"Production complete: {quantity} x {product.name}. "
                f"{len(deducted)} material(s) automatically deducted from inventory."
            )
            result = {'product': product, 'quantity': quantity, 'deducted': deducted, 'new_alerts': new_alerts}
            form = CompleteProductionForm()
    else:
        form = CompleteProductionForm()

    return render(request, 'production/complete_production.html', {'form': form, 'result': result})
