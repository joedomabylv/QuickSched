"""Admin information for emailupload app."""
from django.contrib import admin
from .models import EmailInformation

admin.site.register(EmailInformation)
