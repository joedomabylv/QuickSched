"""Admin information for teachingassistant app."""
from django.contrib import admin
from .models import TA, Holds, Availability, ClassTime


class TAAdmin(admin.ModelAdmin):
    """Admin configuration display."""

    list_display = ['__str__', 'contracted']
    exclude = ['holds_key', 'availability_key']


admin.site.register(TA, TAAdmin)

# these won't be registered in the final product
admin.site.register(Holds)
admin.site.register(Availability)
admin.site.register(ClassTime)
