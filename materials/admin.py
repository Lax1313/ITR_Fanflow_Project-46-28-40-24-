from django.contrib import admin

from .models import Material


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit', 'unit_cost', 'reorder_level', 'is_active')
    search_fields = ('name',)
    list_filter = ('category', 'is_active')
    ordering = ('name',)
