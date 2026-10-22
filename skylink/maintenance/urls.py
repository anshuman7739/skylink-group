from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.home, name='home'),
    path('service-request/', views.service_request, name='service_request'),
    path('success/<str:ref>/', views.success, name='success'),
]
