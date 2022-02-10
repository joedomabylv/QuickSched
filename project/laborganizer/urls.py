"""URL management for LabOrganizer app."""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 'lo' prefix = lab organizer
    path('', views.lo_home, name='lo_home'),
    path('ta_management/', views.lo_ta_management, name='lo_ta_management'),
    path('ta_add/', include("emailupload.urls")),
    path('semester/', views.lo_semester, name='lo_semester'),
    path('new_semester/', views.lo_new_semester, name='lo_new_semester'),
    path('display_semester/', views.lo_display_semester, name='lo_display_semester'),
    path('upload/', views.lo_upload, name='lo_upload'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
