from django.urls import path
from . import views

app_name = 'enrollments'

urlpatterns = [
    path('course/<int:course_pk>/enroll/', views.enroll, name='enroll'),
    path('course/<int:course_pk>/unenroll/', views.unenroll, name='unenroll'),
]

