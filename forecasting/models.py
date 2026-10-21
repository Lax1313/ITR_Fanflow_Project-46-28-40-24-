from django.db import models

from products.models import Product


class DemandForecast(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='forecasts')
    forecast_date = models.DateField()
    predicted_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    model_name = models.CharField(max_length=50, help_text="e.g. RandomForestRegressor")
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, help_text="R^2 on the test set, 0-100")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-forecast_date']
        indexes = [models.Index(fields=['product', 'forecast_date'])]

    def __str__(self):
        return f"{self.product.name} forecast for {self.forecast_date}: {self.predicted_quantity}"
