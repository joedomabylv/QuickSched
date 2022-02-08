"""View management for LabOrganizer app. 'lo' prefix = lab organizer."""
from django.shortcuts import render
from .forms import SemesterForm
from teachingassistant.models import TA


def lo_home(request):
    """Home route."""
    return render(request, 'laborganizer/dashboard.html')


def lo_ta_management(request):
    """TA Management route."""
    # in the future, we should filter which TA's are displayed based on
    # which semester is currently chosen
    # ta = ta.objects.filter()
    tas = TA.objects.all()
    context = {
        'tas': tas,
        }
    return render(request, 'laborganizer/ta_management.html', context)


def lo_ta_add(request):
    """View for LO to add new TA's to the roster."""
    return render(request, 'laborganizer/ta_add.html')


def lo_semester(request):
    """View for semester information."""
    context = {
        # get the name of the semester
        # 'title_tag':
        'form': SemesterForm(),
        }
    return render(request, 'laborganizer/semester.html', context)


def lo_upload(request):
    """View to upload CSV file. Probably going to be deleted, see Andrew."""
    return render(request, 'laborganizer/dashboard.html')
