from django.urls import path

from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_hub, name='hub'),
    path('inventory.csv', views.export_inventory_csv, name='inventory_csv'),
    path('inventory.pdf', views.export_inventory_pdf, name='inventory_pdf'),
    path('suppliers.csv', views.export_suppliers_csv, name='suppliers_csv'),
    path('orders.csv', views.export_orders_csv, name='orders_csv'),
    path('forecast.csv', views.export_forecast_csv, name='forecast_csv'),
    path('risk.csv', views.export_risk_csv, name='risk_csv'),
]
