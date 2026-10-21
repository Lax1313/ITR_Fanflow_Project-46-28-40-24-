"""
Feature engineering for the demand forecasting model.

Uses actual SalesHistory rows from the database -- no synthetic feature
values are invented here.
"""
import pandas as pd

from orders.models import SalesHistory

SEASON_MAP = {'SUMMER': 0, 'MONSOON': 1, 'WINTER': 2, 'SPRING': 3}

FEATURE_COLUMNS = [
    'product_id', 'region_code', 'month', 'year', 'season_code',
    'temperature', 'festival_indicator', 'promotion_indicator',
    'previous_sales', 'previous_month_sales', 'previous_year_sales',
]
TARGET_COLUMN = 'quantity_sold'


def load_sales_dataframe():
    qs = SalesHistory.objects.all().order_by('product_id', 'region', 'date')
    records = list(qs.values(
        'product_id', 'date', 'region', 'quantity_sold', 'temperature',
        'season', 'festival_indicator', 'promotion_indicator',
    ))
    df = pd.DataFrame.from_records(records)
    if df.empty:
        return df
    df['date'] = pd.to_datetime(df['date'])
    return df


def engineer_features(df):
    """
    Adds month/year/season/lag features. Lag features (previous_sales,
    previous_month_sales, previous_year_sales) are computed per
    product+region group, sorted chronologically, so there's no leakage
    from the future into the past.
    """
    df = df.sort_values(['product_id', 'region', 'date']).reset_index(drop=True)

    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['season_code'] = df['season'].map(SEASON_MAP)
    df['festival_indicator'] = df['festival_indicator'].astype(int)
    df['promotion_indicator'] = df['promotion_indicator'].astype(int)

    region_categories = sorted(df['region'].unique().tolist())
    region_map = {r: i for i, r in enumerate(region_categories)}
    df['region_code'] = df['region'].map(region_map)

    group = df.groupby(['product_id', 'region'])['quantity_sold']
    df['previous_sales'] = group.shift(1)
    df['previous_month_sales'] = group.shift(1)
    df['previous_year_sales'] = group.shift(12)

    lag_cols = ['previous_sales', 'previous_month_sales', 'previous_year_sales']
    df[lag_cols] = df[lag_cols].fillna(0)

    return df, region_map
