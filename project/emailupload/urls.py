"""URL management for EmailUpload app."""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 'eu' prefix = email_upload
    path('', views.eu_upload, name='eu_upload'),
    path('cancel_roster', views.cancel_roster, name='cancel_roster'),
    path('confirm_emails', views.confirm_emails, name='confirm_emails'),
]
