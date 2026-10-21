from django.contrib import admin

from .models import RiskAlert


@admin.register(RiskAlert)
class RiskAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'risk_type', 'severity', 'is_resolved', 'created_at')
    list_filter = ('risk_type', 'severity', 'is_resolved')
    ordering = ('-created_at',)
