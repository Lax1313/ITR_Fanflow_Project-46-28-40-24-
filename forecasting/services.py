"""
Django-facing forecasting service. This is the function views/management
commands should call -- it wraps the ml/ module and persists results to
the DemandForecast model.
"""
from decimal import Decimal

from django.db.models import Avg

from orders.models import SalesHistory
from products.models import Product

from .ml.predict import get_model_confidence, predict_demand
from .ml.train_model import train_and_select_best_model
from .models import DemandForecast


def _lag_features(product_id, region):
    qs = SalesHistory.objects.filter(product_id=product_id)
    if region and region != 'All':
        qs = qs.filter(region=region)
    latest = qs.order_by('-date').first()
    value = latest.quantity_sold if latest else 0
    # Simplified: reuse the most recent known sale as the lag proxy. A
    # production system would look up the exact month/year-ago record.
    return value, value, value


def forecast_demand(product_id, forecast_date, region=None):
    """
    1. Load trained model (handled inside predict_demand).
    2. Retrieve relevant recent sales data for lag/context features.
    3. Prepare features.
    4. Generate prediction.
    5. Store prediction in DemandForecast.
    6. Return the saved DemandForecast instance.
    """
    region = region or 'All'
    prev_sales, prev_month, prev_year = _lag_features(product_id, region)

    avg_temp = SalesHistory.objects.filter(product_id=product_id).aggregate(
        avg=Avg('temperature')
    )['avg'] or 30.0

    result = predict_demand(
        product_id, forecast_date, region,
        temperature=avg_temp,
        previous_sales=prev_sales,
        previous_month_sales=prev_month,
        previous_year_sales=prev_year,
    )
    if result is None:
        return None

    predicted_quantity, model_name = result
    confidence = get_model_confidence() or Decimal('0')
    product = Product.objects.get(pk=product_id)

    return DemandForecast.objects.create(
        product=product,
        forecast_date=forecast_date,
        predicted_quantity=Decimal(str(round(predicted_quantity, 2))),
        model_name=model_name,
        confidence_score=Decimal(str(confidence)),
    )


def train_model():
    """Thin wrapper so views/management commands don't import ml.* directly."""
    return train_and_select_best_model()
