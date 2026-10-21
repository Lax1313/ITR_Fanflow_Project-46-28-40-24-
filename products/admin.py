from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_number', 'category', 'selling_price', 'production_capacity', 'is_active')
    search_fields = ('name', 'model_number')
    list_filter = ('category', 'is_active')
    ordering = ('name',)
