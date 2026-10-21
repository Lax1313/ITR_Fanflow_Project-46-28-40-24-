"""
Loads the trained model saved by train_model.py and generates a single
prediction for a given product/date/region.
"""
from pathlib import Path

import joblib
import pandas as pd
from django.conf import settings

from .preprocess import FEATURE_COLUMNS, SEASON_MAP

MODEL_PATH = Path(settings.ML_MODELS_DIR) / 'demand_forecast_model.joblib'


def _season_for_month(month):
    if month in (3, 4, 5):
        return 'SUMMER'
    if month in (6, 7, 8, 9):
        return 'MONSOON'
    if month in (10, 11):
        return 'SPRING'
    return 'WINTER'  # Dec, Jan, Feb


def load_model_bundle():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


def build_feature_row(product_id, forecast_date, region, region_map, temperature=30.0,
                       festival=False, promotion=False, previous_sales=0,
                       previous_month_sales=0, previous_year_sales=0):
    row = {
        'product_id': product_id,
        'region_code': region_map.get(region, 0),
        'month': forecast_date.month,
        'year': forecast_date.year,
        'season_code': SEASON_MAP[_season_for_month(forecast_date.month)],
        'temperature': temperature,
        'festival_indicator': int(festival),
        'promotion_indicator': int(promotion),
        'previous_sales': previous_sales,
        'previous_month_sales': previous_month_sales,
        'previous_year_sales': previous_year_sales,
    }
    return pd.DataFrame([row])[FEATURE_COLUMNS]


def predict_demand(product_id, forecast_date, region='All', **kwargs):
    """Returns (predicted_quantity, model_name) or None if no model is trained yet."""
    bundle = load_model_bundle()
    if bundle is None:
        return None

    X = build_feature_row(product_id, forecast_date, region, bundle['region_map'], **kwargs)
    prediction = bundle['model'].predict(X)[0]
    return max(0.0, float(prediction)), bundle['model_name']


def get_model_confidence():
    bundle = load_model_bundle()
    if bundle is None:
        return None
    return round(bundle.get('r2', 0) * 100, 2)
