from django.contrib import admin

from .models import DemandForecast


@admin.register(DemandForecast)
class DemandForecastAdmin(admin.ModelAdmin):
    list_display = ('product', 'forecast_date', 'predicted_quantity', 'model_name', 'confidence_score')
    list_filter = ('model_name',)
    ordering = ('-forecast_date',)
