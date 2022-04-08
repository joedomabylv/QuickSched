"""Admin information for laborganizer app."""
from django.contrib import admin
from .models import Semester, Lab


class LabAdmin(admin.ModelAdmin):
    """Admin configuration display."""

    list_display = ['__str__', 'semester', 'course_id', 'section', 'instructor']
    list_filter = ['semester', 'instructor']
    readonly_fields = ['days',
                       'course_id',
                       'start_time',
                       'end_time',
                       'semester']


class SemesterAdmin(admin.ModelAdmin):
    """Admin configuration display."""

    list_display = ['__str__', 'semester_time', 'year']
    readonly_fields = ['semester_time', 'year']


admin.site.register(Semester, SemesterAdmin)
admin.site.register(Lab, LabAdmin)
