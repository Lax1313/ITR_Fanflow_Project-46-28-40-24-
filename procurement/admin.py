from django.contrib import admin

from .models import PurchaseOrder, PurchaseOrderItem


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'status', 'total_amount', 'order_date', 'expected_delivery_date')
    list_filter = ('status',)
    inlines = [PurchaseOrderItemInline]
