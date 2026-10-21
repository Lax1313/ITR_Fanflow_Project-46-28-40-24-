from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='list'),
    path('export.csv', views.product_export_csv, name='export_csv'),
    path('add/', views.product_add, name='add'),
    path('<int:pk>/', views.product_detail, name='detail'),
    path('<int:pk>/edit/', views.product_edit, name='edit'),
]
