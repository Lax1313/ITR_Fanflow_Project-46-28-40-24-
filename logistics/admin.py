from django.contrib import admin

from .models import Shipment


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'transport_mode', 'status', 'dispatch_date', 'expected_arrival')
    list_filter = ('status', 'transport_mode')
