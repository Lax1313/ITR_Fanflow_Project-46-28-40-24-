from django.db import models

from products.models import Product


class CustomerOrder(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        IN_PRODUCTION = 'IN_PRODUCTION', 'In Production'
        READY = 'READY', 'Ready'
        SHIPPED = 'SHIPPED', 'Shipped'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        NORMAL = 'NORMAL', 'Normal'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent'

    customer_name = models.CharField(max_length=150)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField()
    order_date = models.DateField()
    required_delivery_date = models.DateField()
    region = models.CharField(max_length=100)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-order_date']

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name} ({self.product.name} x{self.quantity})"


class SalesHistory(models.Model):
    class Season(models.TextChoices):
        SUMMER = 'SUMMER', 'Summer'
        MONSOON = 'MONSOON', 'Monsoon'
        WINTER = 'WINTER', 'Winter'
        SPRING = 'SPRING', 'Spring'

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales_history')
    date = models.DateField()
    region = models.CharField(max_length=100)
    quantity_sold = models.PositiveIntegerField()
    temperature = models.FloatField(help_text="Avg temperature (Celsius) for the period")
    season = models.CharField(max_length=10, choices=Season.choices)
    festival_indicator = models.BooleanField(default=False)
    promotion_indicator = models.BooleanField(default=False)

    class Meta:
        ordering = ['date']
        indexes = [models.Index(fields=['product', 'date'])]

    def __str__(self):
        return f"{self.product.name} - {self.date} - {self.quantity_sold} units"
