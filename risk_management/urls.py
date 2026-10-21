from django.urls import path

from . import views

app_name = 'risk_management'

urlpatterns = [
    path('', views.risk_list, name='list'),
    path('scan/', views.risk_scan, name='scan'),
    path('<int:pk>/resolve/', views.risk_resolve, name='resolve'),
]
