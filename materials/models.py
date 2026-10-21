from django.db import models


class Material(models.Model):
    class Category(models.TextChoices):
        ELECTRICAL = 'ELECTRICAL', 'Electrical'
        MECHANICAL = 'MECHANICAL', 'Mechanical'
        PACKAGING = 'PACKAGING', 'Packaging'
        RAW_METAL = 'RAW_METAL', 'Raw Metal'
        PLASTIC = 'PLASTIC', 'Plastic'
        OTHER = 'OTHER', 'Other'

    class Unit(models.TextChoices):
        PIECE = 'PCS', 'Pieces'
        KG = 'KG', 'Kilograms'
        METER = 'M', 'Meters'
        LITER = 'L', 'Liters'
        SET = 'SET', 'Set'

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    unit = models.CharField(max_length=10, choices=Unit.choices, default=Unit.PIECE)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.PositiveIntegerField(default=0)
    safety_stock = models.PositiveIntegerField(default=0)
    maximum_stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_unit_display()})"
