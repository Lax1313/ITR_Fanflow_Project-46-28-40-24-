from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import section_required

from .models import RiskAlert
from .services import run_all_risk_checks


@section_required('risk')
def risk_list(request):
    alerts = RiskAlert.objects.filter(is_resolved=False)
    resolved_count = RiskAlert.objects.filter(is_resolved=True).count()
    return render(request, 'risk/risk_list.html', {'alerts': alerts, 'resolved_count': resolved_count})


@section_required('risk')
def risk_scan(request):
    if request.method == 'POST':
        created = run_all_risk_checks()
        if created:
            messages.success(request, f"Risk scan complete: {len(created)} new alert(s) found.")
        else:
            messages.info(request, "Risk scan complete: no new risks detected.")
    return redirect('risk_management:list')


@section_required('risk')
def risk_resolve(request, pk):
    alert = get_object_or_404(RiskAlert, pk=pk)
    alert.is_resolved = True
    alert.save(update_fields=['is_resolved'])
    messages.success(request, "Alert marked as resolved.")
    return redirect('risk_management:list')
