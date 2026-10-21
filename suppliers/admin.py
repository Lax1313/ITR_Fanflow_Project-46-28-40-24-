from django.contrib import admin

from .models import Supplier, SupplierMaterial


class SupplierMaterialInline(admin.TabularInline):
    model = SupplierMaterial
    extra = 1


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'quality_score', 'reliability_score', 'status')
    list_filter = ('status',)
    search_fields = ('name',)
    inlines = [SupplierMaterialInline]


@admin.register(SupplierMaterial)
class SupplierMaterialAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'material', 'unit_price', 'lead_time_days', 'reliability_score')
    list_filter = ('supplier',)
