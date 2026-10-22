from django.urls import path
from . import views

app_name = 'academy'

urlpatterns = [
    path('', views.home, name='home'),
    path('course-admission/', views.course_admission, name='course_admission'),
    path('success/<str:ref>/', views.success, name='success'),
]
