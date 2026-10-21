from django.urls import path

from . import views

app_name = 'production'

urlpatterns = [
    path('bom/', views.bom_list, name='bom_list'),
    path('bom/add/', views.bom_add, name='bom_add'),
    path('bom/<int:pk>/', views.bom_detail, name='bom_detail'),
    path('bom/<int:pk>/edit/', views.bom_edit, name='bom_edit'),
    path('mrp/', views.mrp_calculator, name='mrp_calculator'),
    path('complete/', views.complete_production, name='complete_production'),
]
