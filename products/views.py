import csv

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import section_required

from .forms import ProductForm
from .models import Product


def _filtered_products(request):
    products = Product.objects.all()
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    if query:
        from django.db.models import Q
        products = products.filter(Q(name__icontains=query) | Q(model_number__icontains=query))
    if category:
        products = products.filter(category=category)

    return products


@section_required('products')
def product_list(request):
    products = _filtered_products(request)
    categories = [(c, c) for c in Product.objects.order_by('category').values_list('category', flat=True).distinct()]
    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
    })


@section_required('products')
def product_export_csv(request):
    products = _filtered_products(request)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'
    writer = csv.writer(response)
    writer.writerow(['Model Number', 'Name', 'Category', 'Selling Price', 'Production Capacity', 'Power Rating', 'Active'])
    for p in products:
        writer.writerow([p.model_number, p.name, p.category, p.selling_price, p.production_capacity, p.power_rating, p.is_active])
    return response


@section_required('products')
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.name}' created.")
            return redirect('products:detail', pk=product.pk)
    else:
        form = ProductForm()
    return render(request, 'generic_form.html', {'form': form, 'title': 'Add Product'})


@section_required('products')
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    from production.services import get_active_bom
    bom = get_active_bom(product)
    return render(request, 'products/product_detail.html', {'product': product, 'bom': bom})


@section_required('products')
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product '{product.name}' updated.")
            return redirect('products:detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'generic_form.html', {'form': form, 'title': f'Edit {product.name}'})
