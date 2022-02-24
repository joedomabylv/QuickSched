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
    path('semester_management/', views.lo_semester_management,
         name='lo_semester_management'),
    path('generate_schedule/', views.lo_generate_schedule,
         name='lo_generate_schedule'),
    path('upload/', views.lo_upload, name='lo_upload'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
