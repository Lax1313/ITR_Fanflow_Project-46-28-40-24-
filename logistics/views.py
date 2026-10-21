from django.shortcuts import get_object_or_404, render

from accounts.decorators import section_required

from .models import Shipment


@section_required('logistics')
def shipment_list(request):
    shipments = Shipment.objects.select_related('supplier', 'purchase_order').all()
    return render(request, 'logistics/shipment_list.html', {'shipments': shipments})


@section_required('logistics')
def shipment_detail(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)
    return render(request, 'logistics/shipment_detail.html', {'shipment': shipment})
