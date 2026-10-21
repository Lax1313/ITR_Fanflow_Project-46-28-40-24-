from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import get_chart_data, get_kpis, get_smart_insights


@login_required
def dashboard_home(request):
    context = {
        'kpis': get_kpis(),
        'charts': get_chart_data(),
        'insights': get_smart_insights(),
    }
    return render(request, 'dashboard/dashboard.html', context)
