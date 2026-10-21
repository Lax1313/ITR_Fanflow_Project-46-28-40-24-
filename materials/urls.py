from django.urls import path

from . import views

app_name = 'materials'

urlpatterns = [
    path('', views.material_list, name='list'),
    path('add/', views.material_add, name='add'),
    path('<int:pk>/', views.material_detail, name='detail'),
    path('<int:pk>/edit/', views.material_edit, name='edit'),
    path('<int:material_id>/suppliers/', views.material_supplier_comparison, name='supplier_comparison'),
]
