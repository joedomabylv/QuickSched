"""Admin information for teachingassistant app."""
from django.contrib import admin
from .models import TA


class TAAdmin(admin.ModelAdmin):
    """Admin configuration display."""

    list_display = ['__str__', 'contracted']


admin.site.register(TA, TAAdmin)
