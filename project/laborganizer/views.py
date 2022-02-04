"""View management for LabOrganizer app. 'lo' prefix = lab organizer."""
from django.shortcuts import render


def lo_home(request):
    """Home route."""
    return render(request, 'laborganizer/dashboard.html')


def lo_ta_management(request):
    """TA Management route."""
    return render(request, 'laborganizer/ta_management.html')


def lo_ta_add(request):
    """View for LO to add new TA's to the roster."""
    return render(request, 'laborganizer/ta_add.html')


def lo_semester(request):
    """View for semester information."""
    return render(request, 'laborganizer/semester.html')


def lo_upload(request):
    """View to upload CSV file. Probably going to be deleted, see Andrew."""
    return render(request, 'laborganizer/dashboard.html')
