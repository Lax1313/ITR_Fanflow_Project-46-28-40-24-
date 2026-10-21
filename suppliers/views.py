import csv

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import section_required

from .forms import SupplierForm, SupplierMaterialForm
from .models import Supplier, SupplierMaterial


def _filtered_suppliers(request):
    suppliers = Supplier.objects.all()
    query = request.GET.get('q', '').strip()
    status = request.GET.get('category', '').strip()  # reuses the shared filter_bar's "category" param

    if query:
        from django.db.models import Q
        suppliers = suppliers.filter(
            Q(name__icontains=query) | Q(location__icontains=query) | Q(contact_person__icontains=query)
        )
    if status:
        suppliers = suppliers.filter(status=status)

    return suppliers


@section_required('suppliers')
def supplier_list(request):
    suppliers = _filtered_suppliers(request)
    statuses = list(Supplier.Status.choices)
    return render(request, 'suppliers/supplier_list.html', {'suppliers': suppliers, 'statuses': statuses})


@section_required('suppliers')
def supplier_export_csv(request):
    suppliers = _filtered_suppliers(request)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="suppliers.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Location', 'Contact', 'Email', 'Phone', 'Quality Score', 'Reliability Score', 'Status'])
    for s in suppliers:
        writer.writerow([s.name, s.location, s.contact_person, s.email, s.phone, s.quality_score, s.reliability_score, s.status])
    return response


@section_required('suppliers')
def supplier_add(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f"Supplier '{supplier.name}' created.")
            return redirect('suppliers:detail', pk=supplier.pk)
    else:
        form = SupplierForm()
    return render(request, 'generic_form.html', {'form': form, 'title': 'Add Supplier'})


@section_required('suppliers')
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    materials = supplier.materials_supplied.select_related('material').all()
    return render(request, 'suppliers/supplier_detail.html', {'supplier': supplier, 'materials': materials})


@section_required('suppliers')
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, f"Supplier '{supplier.name}' updated.")
            return redirect('suppliers:detail', pk=supplier.pk)
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'generic_form.html', {'form': form, 'title': f'Edit {supplier.name}'})


@section_required('suppliers')
def supplier_material_edit(request, pk):
    sm = get_object_or_404(SupplierMaterial, pk=pk)
    if request.method == 'POST':
        form = SupplierMaterialForm(request.POST, instance=sm)
        if form.is_valid():
            form.save()
            messages.success(request, f"Pricing updated for {sm.material.name} from {sm.supplier.name}.")
            return redirect('suppliers:detail', pk=sm.supplier.pk)
    else:
        form = SupplierMaterialForm(instance=sm)
    return render(request, 'generic_form.html', {'form': form, 'title': f'Edit {sm.material.name} pricing'})
