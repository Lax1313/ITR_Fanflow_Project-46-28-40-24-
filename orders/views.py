from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import section_required

from .forms import CustomerOrderForm
from .models import CustomerOrder, SalesHistory


@section_required('orders')
def order_list(request):
    orders = CustomerOrder.objects.select_related('product').all()
    return render(request, 'orders/order_list.html', {'orders': orders})


@section_required('orders')
def order_add(request):
    if request.method == 'POST':
        form = CustomerOrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            messages.success(request, f"Order for {order.customer_name} created.")
            return redirect('orders:detail', pk=order.pk)
    else:
        form = CustomerOrderForm()
    return render(request, 'generic_form.html', {'form': form, 'title': 'Add Customer Order'})


@section_required('orders')
def order_detail(request, pk):
    order = get_object_or_404(CustomerOrder, pk=pk)
    return render(request, 'orders/order_detail.html', {'order': order})


@section_required('orders')
def sales_history_list(request):
    history = SalesHistory.objects.select_related('product').order_by('-date')[:200]
    return render(request, 'orders/sales_history_list.html', {'history': history})


@section_required('orders')
def order_edit(request, pk):
    order = get_object_or_404(CustomerOrder, pk=pk)
    if request.method == 'POST':
        form = CustomerOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f"Order #{order.id} updated.")
            return redirect('orders:detail', pk=order.pk)
    else:
        form = CustomerOrderForm(instance=order)
    return render(request, 'generic_form.html', {'form': form, 'title': f'Edit Order #{order.id}'})
