"""Admin information for teachingassistant app."""
from django.contrib import admin
from .models import TA


class TAAdmin(admin.ModelAdmin):
    """Admin configuration display."""

    list_display = ['__str__', 'student_id', 'year']
    list_filter = ['year']
    exclude = ['holds_key', 'availability_key', 'scores']
    readonly_fields = ['year',
                       'experience',
                       'assigned_labs',
                       'assigned_semesters']


admin.site.register(TA, TAAdmin)
