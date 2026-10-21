from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='list'),
    path('add/', views.order_add, name='add'),
    path('<int:pk>/', views.order_detail, name='detail'),
    path('<int:pk>/edit/', views.order_edit, name='edit'),
    path('sales-history/', views.sales_history_list, name='sales_history'),
]
