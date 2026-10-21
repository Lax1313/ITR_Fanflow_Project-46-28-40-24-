from django.contrib import admin

from .models import AssistantQuery


@admin.register(AssistantQuery)
class AssistantQueryAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'created_at')
    ordering = ('-created_at',)
