"""Admin information for teachingassistant app."""
from django.contrib import admin
from .models import TA, Holds, Availability


class TAAdmin(admin.ModelAdmin):
    """Admin configuration display."""

    list_display = ['__str__', 'contracted']


admin.site.register(TA, TAAdmin)

# these won't be registered in the final product
admin.site.register(Holds)
admin.site.register(Availability)
