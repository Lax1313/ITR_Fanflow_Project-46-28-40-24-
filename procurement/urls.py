from django.urls import path

from . import views

app_name = 'procurement'

urlpatterns = [
    path('recommendations/', views.recommendations, name='recommendations'),
    path('recommendations/<int:material_id>/create-po/', views.create_po_from_recommendation, name='create_po'),
    path('purchase-orders/', views.po_list, name='po_list'),
    path('purchase-orders/<int:pk>/', views.po_detail, name='po_detail'),
    path('purchase-orders/<int:pk>/status/', views.po_update_status, name='po_update_status'),
]
