from datetime import date, timedelta

from django.core.management.base import BaseCommand

from forecasting.services import forecast_demand
from products.models import Product


class Command(BaseCommand):
    help = 'Generates a 30-day-ahead demand forecast for every active product using the trained model.'

    def handle(self, *args, **options):
        forecast_date = date.today() + timedelta(days=30)
        created = 0
        for product in Product.objects.filter(is_active=True):
            result = forecast_demand(product.id, forecast_date)
            if result:
                self.stdout.write(f"{product.name}: {result.predicted_quantity} units on {forecast_date} ({result.model_name})")
                created += 1
            else:
                self.stdout.write(self.style.WARNING(f"{product.name}: no trained model available."))
        self.stdout.write(self.style.SUCCESS(f"\nGenerated {created} forecasts."))
