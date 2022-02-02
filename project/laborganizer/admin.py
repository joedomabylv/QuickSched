"""Admin information for laborganizer app."""
from django.contrib import admin
from .models import Semester, Lab


class LabAdmin(admin.ModelAdmin):
    """Admin configuration display."""

    list_display = ['__str__', 'semester', 'staffed']
    list_filter = ['semester']


admin.site.register(Semester)
admin.site.register(Lab, LabAdmin)
