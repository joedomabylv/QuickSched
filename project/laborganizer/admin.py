"""Admin information for laborganizer app."""
from django.contrib import admin
from .models import Semester, Lab


admin.site.register(Semester)
admin.site.register(Lab)
