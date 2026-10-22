from django.urls import path
from . import views

app_name = 'staffing'

urlpatterns = [
    path('', views.home, name='home'),
    path('employer-enquiry/', views.employer_enquiry, name='employer_enquiry'),
    path('careers/', views.job_application, name='job_application'),
    path('success/<str:ref>/', views.success, name='success'),
]
