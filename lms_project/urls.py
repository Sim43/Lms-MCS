"""
URL configuration for lms_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('courses.urls')),
    path('accounts/', include('accounts.urls')),
    path('lessons/', include('lessons.urls')),
    path('enrollments/', include('enrollments.urls')),
    path('dashboard/', include('dashboards.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Error handlers
handler404 = 'courses.views.custom_404'
handler500 = 'courses.views.custom_500'

