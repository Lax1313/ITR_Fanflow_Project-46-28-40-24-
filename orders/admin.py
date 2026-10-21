from django.contrib import admin

from .models import CustomerOrder, SalesHistory


@admin.register(CustomerOrder)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'product', 'quantity', 'status', 'priority', 'order_date')
    list_filter = ('status', 'priority', 'region')
    search_fields = ('customer_name',)


@admin.register(SalesHistory)
class SalesHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'date', 'region', 'quantity_sold', 'season')
    list_filter = ('season', 'region', 'festival_indicator', 'promotion_indicator')
    ordering = ('-date',)
