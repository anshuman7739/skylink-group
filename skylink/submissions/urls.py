from django.urls import path
from . import views

app_name = 'submissions'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.admin_logout_view, name='admin_logout'),
    path('submission/<uuid:pk>/', views.submission_detail, name='detail'),
    path('export/', views.export_csv_view, name='export'),
    path('settings/', views.website_settings_view, name='settings'),
]
