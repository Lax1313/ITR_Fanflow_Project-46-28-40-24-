from django.urls import path

from . import views

app_name = 'forecasting'

urlpatterns = [
    path('', views.forecasting_home, name='home'),
    path('train/', views.train_forecast_model_view, name='train'),
    path('run/', views.run_forecast_view, name='run'),
]
