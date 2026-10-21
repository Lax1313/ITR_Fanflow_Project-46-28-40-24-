from django.contrib import admin

from .models import BOM, BOMItem


class BOMItemInline(admin.TabularInline):
    model = BOMItem
    extra = 1


@admin.register(BOM)
class BOMAdmin(admin.ModelAdmin):
    list_display = ('product', 'version', 'is_active', 'created_at')
    list_filter = ('is_active',)
    inlines = [BOMItemInline]
