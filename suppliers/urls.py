from django.urls import path

from . import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.supplier_list, name='list'),
    path('export.csv', views.supplier_export_csv, name='export_csv'),
    path('add/', views.supplier_add, name='add'),
    path('<int:pk>/', views.supplier_detail, name='detail'),
    path('<int:pk>/edit/', views.supplier_edit, name='edit'),
    path('material-pricing/<int:pk>/edit/', views.supplier_material_edit, name='material_edit'),
]
