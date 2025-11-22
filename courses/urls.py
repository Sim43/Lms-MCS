from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('courses/create/', views.instructor_course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.instructor_course_edit, name='course_edit'),
    path('courses/<int:pk>/delete/', views.instructor_course_delete, name='course_delete'),
]

