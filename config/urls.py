"""
Root URL configuration for the FanFlow project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from materials import views as material_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('products/', include('products.urls', namespace='products')),
    path('materials/', include('materials.urls', namespace='materials')),
    path('production/', include('production.urls', namespace='production')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('inventory/', include('inventory.urls', namespace='inventory')),
    path('suppliers/', include('suppliers.urls', namespace='suppliers')),
    path('forecasting/', include('forecasting.urls', namespace='forecasting')),
    path('procurement/', include('procurement.urls', namespace='procurement')),
    path('logistics/', include('logistics.urls', namespace='logistics')),
    path('risk/', include('risk_management.urls', namespace='risk_management')),
    path('analytics/', include('analytics.urls', namespace='analytics')),
    path('ai-assistant/', include('ai_assistant.urls', namespace='ai_assistant')),
    path('reports/', include('reports.urls', namespace='reports')),
    path('notifications/', include('notifications.urls', namespace='notifications')),

    # Root redirects to the dashboard (which redirects to login if needed)
    path('', RedirectView.as_view(pattern_name='dashboard:home', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
