"""
Trains and compares Linear Regression vs Random Forest Regressor on
SalesHistory data, evaluates MAE/RMSE/R2 using a time-aware (not shuffled)
train/test split, and saves the best-performing model with Joblib.
"""
from pathlib import Path

import joblib
import numpy as np
from django.conf import settings
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .preprocess import FEATURE_COLUMNS, TARGET_COLUMN, engineer_features, load_sales_dataframe

MODEL_PATH = Path(settings.ML_MODELS_DIR) / 'demand_forecast_model.joblib'


def train_and_select_best_model():
    df = load_sales_dataframe()
    if df.empty or len(df) < 30:
        return {
            'success': False,
            'reason': 'Not enough sales history to train a model (need at least 30 rows). '
                      'Run `python manage.py generate_demo_data` first.',
        }

    df, region_map = engineer_features(df)
    df = df.sort_values('date').reset_index(drop=True)

    # Time-aware split: last 20% chronologically becomes the test set.
    # No random shuffling, to avoid leaking future data into training.
    split_idx = int(len(df) * 0.8)
    train_df, test_df = df.iloc[:split_idx], df.iloc[split_idx:]

    X_train, y_train = train_df[FEATURE_COLUMNS], train_df[TARGET_COLUMN]
    X_test, y_test = test_df[FEATURE_COLUMNS], test_df[TARGET_COLUMN]

    candidates = {
        'LinearRegression': LinearRegression(),
        'RandomForestRegressor': RandomForestRegressor(
            n_estimators=200, max_depth=10, random_state=42, n_jobs=-1,
        ),
    }

    results = {}
    for name, model in candidates.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        results[name] = {
            'model': model,
            'mae': float(mean_absolute_error(y_test, preds)),
            'rmse': float(np.sqrt(mean_squared_error(y_test, preds))),
            'r2': float(r2_score(y_test, preds)),
        }

    best_name = min(results, key=lambda k: results[k]['mae'])
    best = results[best_name]

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        'model': best['model'],
        'model_name': best_name,
        'region_map': region_map,
        'feature_columns': FEATURE_COLUMNS,
        'r2': best['r2'],
    }, MODEL_PATH)

    return {
        'success': True,
        'best_model': best_name,
        'model_path': str(MODEL_PATH),
        'metrics': {name: {'mae': r['mae'], 'rmse': r['rmse'], 'r2': r['r2']} for name, r in results.items()},
        'training_rows': len(train_df),
        'test_rows': len(test_df),
    }
