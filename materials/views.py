from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import section_required
from inventory.models import Inventory
from inventory.services import calculate_available_stock
from suppliers.services import calculate_supplier_scores_for_material

from .forms import MaterialForm
from .models import Material


@section_required('materials')
def material_list(request):
    materials = Material.objects.all()
    rows = []
    for m in materials:
        inv, _ = Inventory.objects.get_or_create(material=m)
        rows.append({
            'material': m,
            'available': calculate_available_stock(inv),
            'reorder_level': inv.reorder_level,
            'short': calculate_available_stock(inv) < inv.reorder_level,
        })
    return render(request, 'materials/material_list.html', {'rows': rows})


@section_required('materials')
def material_add(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            material = form.save()
            Inventory.objects.get_or_create(
                material=material,
                defaults={
                    'reorder_level': material.reorder_level,
                    'safety_stock': material.safety_stock,
                    'maximum_stock': material.maximum_stock,
                },
            )
            messages.success(request, f"Material '{material.name}' created.")
            return redirect('materials:detail', pk=material.pk)
    else:
        form = MaterialForm()
    return render(request, 'generic_form.html', {'form': form, 'title': 'Add Material'})


@section_required('materials')
def material_detail(request, pk):
    material = get_object_or_404(Material, pk=pk)
    inventory, _ = Inventory.objects.get_or_create(material=material)
    return render(request, 'materials/material_detail.html', {
        'material': material,
        'inventory': inventory,
        'available': calculate_available_stock(inventory),
    })


@section_required('suppliers')
def material_supplier_comparison(request, material_id):
    material = get_object_or_404(Material, pk=material_id)
    scores = calculate_supplier_scores_for_material(material)
    return render(request, 'materials/supplier_comparison.html', {
        'material': material,
        'scores': scores,
    })


@section_required('materials')
def material_edit(request, pk):
    material = get_object_or_404(Material, pk=pk)
    inventory, _ = Inventory.objects.get_or_create(material=material)

    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            material = form.save()
            # Keep the linked Inventory row's thresholds in sync so edits here
            # actually take effect on shortage/reorder calculations.
            inventory.reorder_level = material.reorder_level
            inventory.safety_stock = material.safety_stock
            inventory.maximum_stock = material.maximum_stock
            inventory.save()
            messages.success(request, f"Material '{material.name}' updated.")
            return redirect('materials:detail', pk=material.pk)
    else:
        form = MaterialForm(instance=material)
    return render(request, 'generic_form.html', {'form': form, 'title': f'Edit {material.name}'})
