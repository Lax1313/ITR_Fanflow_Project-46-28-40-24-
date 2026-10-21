from django.contrib import admin

from .models import Inventory, InventoryTransaction


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('material', 'current_stock', 'reserved_stock', 'incoming_stock', 'reorder_level', 'safety_stock')
    search_fields = ('material__name',)


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('material', 'transaction_type', 'quantity', 'date')
    list_filter = ('transaction_type',)
    ordering = ('-date',)
