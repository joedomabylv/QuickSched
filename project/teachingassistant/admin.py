"""Admin information for teachingassistant app."""
from django.contrib import admin
from .models import TA, Holds, Availability
from django import forms
from laborganizer.models import Lab


class AssignmentForm(forms.ModelForm):
    """Assignment form for each TA."""

    assignments = forms.ModelMultipleChoiceField(
        queryset=Lab.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )


class TAAdmin(admin.ModelAdmin):
    """Admin configuration display."""

    list_display = ['__str__', 'contracted']
    form = AssignmentForm


admin.site.register(TA, TAAdmin)

# these won't be registered in the final product
admin.site.register(Holds)
admin.site.register(Availability)
