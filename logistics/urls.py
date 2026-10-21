from django.urls import path

from . import views

app_name = 'logistics'

urlpatterns = [
    path('', views.shipment_list, name='list'),
    path('<int:pk>/', views.shipment_detail, name='detail'),
]
