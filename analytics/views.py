from django.shortcuts import render

from accounts.decorators import section_required
from dashboard.services import get_chart_data, get_kpis


@section_required('analytics')
def analytics_home(request):
    return render(request, 'analytics/analytics.html', {
        'kpis': get_kpis(),
        'charts': get_chart_data(),
    })
