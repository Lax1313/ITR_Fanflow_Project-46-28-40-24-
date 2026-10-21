from datetime import date, timedelta

from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.decorators import section_required
from products.models import Product

from .models import DemandForecast
from .services import forecast_demand, train_model


@section_required('forecasting')
def forecasting_home(request):
    forecasts = DemandForecast.objects.select_related('product').all()[:30]
    products = Product.objects.filter(is_active=True)
    from .ml.predict import load_model_bundle
    model_trained = load_model_bundle() is not None
    return render(request, 'forecasting/forecasting_home.html', {
        'forecasts': forecasts,
        'products': products,
        'model_trained': model_trained,
    })


@section_required('forecasting')
def train_forecast_model_view(request):
    if request.method == 'POST':
        result = train_model()
        if result['success']:
            messages.success(
                request,
                f"Trained successfully. Best model: {result['best_model']} "
                f"(MAE {result['metrics'][result['best_model']]['mae']:.2f}, "
                f"R² {result['metrics'][result['best_model']]['r2']:.3f})."
            )
        else:
            messages.error(request, result['reason'])
    return redirect('forecasting:home')


@section_required('forecasting')
def run_forecast_view(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        days_ahead = int(request.POST.get('days_ahead', 30))
        forecast_date = date.today() + timedelta(days=days_ahead)
        result = forecast_demand(product_id, forecast_date)
        if result:
            messages.success(request, f"Forecast generated: {result.predicted_quantity} units for {result.product.name} on {result.forecast_date}.")
        else:
            messages.error(request, "No trained model available yet. Train the model first.")
    return redirect('forecasting:home')
