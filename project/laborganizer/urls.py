"""URL management for LabOrganizer app."""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 'lo' prefix = lab organizer
    path('', views.lo_home, name='lo_home'),
    path('select_semester', views.lo_select_semester,
         name='lo_select_semester'),
    path('ta_management/', views.lo_ta_management, name='lo_ta_management'),
    path('ta_add/', include("emailupload.urls")),
    path('semester_management/', views.lo_semester_management,
         name='lo_semester_management'),
    path('generate_schedule', views.lo_generate_schedule,
         name='lo_generate_schedule'),
    path('edit_lab', views.lo_edit_lab, name='lo_edit_lab'),
    path('allow_ta_edit', views.lo_allow_ta_edit, name='lo_allow_ta_edit'),
    path('assign_to_template', views.lo_assign_to_template,
         name='lo_assign_to_template'),
    path('select_schedule_version', views.lo_select_schedule_version,
         name='lo_select_schedule_version'),
    path('propogate_schedule', views.lo_propogate_schedule,
         name='lo_propogate_schedule'),
    path('new_semester', views.lo_new_semester,
         name='lo_new_semester'),
    path('update_ta_semesters', views.lo_update_ta_semesters,
         name='lo_update_ta_semesters'),
    path('ta_management/flip_contract_status', views.lo_flip_contract_status,
         name='lo_flip_contract_status'),
    path('upload/', views.lo_upload, name='lo_upload'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
