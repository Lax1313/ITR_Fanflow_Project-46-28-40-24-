from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=150)
    model_number = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=100, default='Ceiling Fan')
    description = models.TextField(blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    production_capacity = models.PositiveIntegerField(help_text="Units producible per month")
    power_rating = models.CharField(max_length=30, help_text="e.g. 75W", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.model_number})"
