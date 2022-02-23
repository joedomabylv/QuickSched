"""View management for LabOrganizer app. 'lo' prefix = lab organizer."""
from django.shortcuts import render, redirect
from .forms import NewSemesterForm
from teachingassistant.models import TA, ScorePair
from .models import Semester, Lab
from django.contrib import messages
from laborganizer.lo_utils import (get_semester_years,
                                   get_semester_times,
                                   get_current_semester,
                                   get_tas_by_semester)


def lo_home(request):
    """Home route for the Lab Organizer dashboard."""
    """
    TODO:

    fix the display of the selections for times/years.
    we should have it where you select a year first, then
    it gives you the available times to choose from. i don't know how
    to do that.

    figure out what to display when it's a POST but no data. meaning, if a LO
    chooses a lab that doesnt exist to display, nothing get's sent through, but
    it's still a POST request.
    """
    # check for post request
    if request.method == 'POST':
        selected_year = request.POST.get('semester_year')
        selected_time = request.POST.get('semester_time')
        labs = Lab.objects.filter(semester__year=selected_year,
                                  semester__semester_time=selected_time)
        tas = get_tas_by_semester(selected_time, selected_year)
        current_semester = (selected_time, selected_year)

    else:
        current_semester = get_current_semester()
        labs = Lab.objects.filter(semester__year=current_semester[1],
                                  semester__semester_time=current_semester[0])

    all_semester_years = get_semester_years()
    all_semester_times = get_semester_times()

    # NOTE: In the future, we only want to send information into this view
    #       relevant to the selected semester. This way, when an LO has 9000
    #       TA's/labs, we're not scraping the whole database.
    context = {
        'labs': labs,
        'tas': tas,
        'semester_years': all_semester_years,
        'semester_times': all_semester_times,
        'current_semester': current_semester,
    }

    if len(labs) == 0:
        messages.warning(request, 'No labs in the selected semester!')
        return render(request, 'laborganizer/dashboard.html', context)
    return render(request, 'laborganizer/dashboard.html', context)


def lo_assign_ta(request):
    """Handle requests to assign a TA to a lab."""
    if request.method == 'POST':
        print('got a post request from lo_assign_ta')

    return redirect('lo_home')


def lo_ta_management(request):
    """TA Management route."""
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
    labs = Lab.objects.all()
    semesters = Semester.objects.all()

    context = {
        # get the name of the semester
        # 'title_tag':
        'semesters': semesters,
        'new_semester_form': NewSemesterForm(),
        }
    return render(request, 'laborganizer/semester.html', context)


def lo_new_semester(request):
    """Handle the new semester form submitted by a user."""
    if request.method == "POST":
        new_year = request.POST.get('year')
        new_semester_time = request.POST['semester_time']

    current_semesters = Semester.objects.all()

    semester_exists = False

    # check if the requested semester already exists within the database
    for semester in current_semesters:
        if (semester.year == new_year and
            semester.semester_time == new_semester_time):
            semester_exists = True

    # handle result
    if semester_exists:
        # do not add the semester, inform the user it exists
        messages.warning(request, 'This semester already exists!')
        return redirect('lo_semester')
    else:
        # add the semester
        Semester.objects.create(year=new_year, semester_time=new_semester_time)
        messages.success(request, 'Semester successfully added!')

    return render(request, 'laborganizer/dashboard.html')


def lo_display_semester(request):
    """Display information regarding a single semester."""
    if request.method == "POST":
        semester = request.POST.get('semester_selection')

        semester_time = semester[:3]
        semester_year = semester[3:]

        labs = Lab.objects.all()
        all_semesters = Semester.objects.all()
        select_labs = []

        for lab in labs:
            if (lab.semester is not None and
                lab.semester.year == semester_year and
                lab.semester.semester_time == semester_time):
                select_labs.append(lab)


        context = {
            'semesters': all_semesters,
            'labs': select_labs,
        }
        return render(request, 'laborganizer/semester.html', context)
    return render(request, 'laborganizer/dashboard.html')


def lo_upload(request):
    """View to upload CSV file. Probably going to be deleted, see Andrew."""
    return render(request, 'laborganizer/dashboard.html')
