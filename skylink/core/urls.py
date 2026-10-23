from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.all_services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('contact/success/<str:ref>/', views.contact_success, name='contact_success'),
    path('track/', views.track_status, name='track_status'),
    path('track/<str:ref>/', views.track_status, name='track_status_detail'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms, name='terms'),
]
