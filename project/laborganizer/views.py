"""
View management for LabOrganizer app. 'lo' prefix = lab organizer.

Variables used throughout LO dashboard:
'labs': used to display in the center console
'tas': used to display available options in the 'TA Selector' sidebar
'semester_years': used to display choices for years in 'Semester Select'
                  sidebar
'semester_times': used to display choices for times in 'Semester Select'
                  sidebar
'current_semester': used to display which semester is currently chosen/active
"""
from django.shortcuts import render, redirect
from .forms import NewSemesterForm
from teachingassistant.models import TA
from .models import Semester, Lab
from django.contrib import messages
from laborganizer.lo_utils import (get_semester_years,
                                   get_semester_times,
                                   get_current_semester,
                                   get_tas_by_semester)


def lo_home(request):
    """
    Home route for the Lab Organizer dashboard.

    Displays data relevant to the active semester based on the time of year.
    """
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

    # establish current semester time/year
    current_semester = get_current_semester()

    # get all labs for the current semester
    labs = Lab.objects.filter(semester__semester_time=current_semester['time'],
                              semester__year=current_semester['year'])

    # get all TA's assigned to that semester
    tas = get_tas_by_semester(current_semester['time'],
                              current_semester['year'])

    # get all existing semester years for selection purposes in the sidebar
    all_semester_years = get_semester_years()

    # get all existing semester times for selection purposes in the sidebar
    all_semester_times = get_semester_times()

    # instantiate context variable
    context = {
        'labs': labs,
        'tas': tas,
        'semester_years': all_semester_years,
        'semester_times': all_semester_times,
        'current_semester': current_semester,
    }

    if len(labs) == 0:
        messages.warning(request, 'No labs in the current semester!')

    return render(request, 'laborganizer/dashboard.html', context)


def lo_generate_schedule(request):
    """
    View for generating TA schedule via LO command, from the TA Selector.

    When the LO chooses new TA's from the left-hand contracted/uncontracted
    TA list, display template scheduling including those chosen TA's.
    """
    if request.method == 'POST':
        # get the student id's of all selected TA's
        ta_ids = request.POST.getlist('checks[]')
        print(ta_ids)

        # get the current semester
        # NOTE: THIS CURRENTLY GETS THE CURRENT SEMESTER BASED ON REAL TIME,
        #       NOT A SEMESTER CHOSEN BY THE LO
        # current_semester = get_current_semester()

        # using those TA's, populate a TemplateSchedule object from
        # optimization.models
        # generate_by_selection()

        # get all the labs from the generated schedule
        # labs = labs.from.that.schedule

        # get all TA's for the currently selected semester
        # tas = get_tas_by_semester(time, year)

        # get all existing semester years for selection purposes in the sidebar
        all_semester_years = get_semester_years()

        # get all existing semester times for selection purposes in the sidebar
        all_semester_times = get_semester_times()

        context = {
            # 'labs': labs,
            # 'tas': tas,
            'semester_years': all_semester_years,
            'semester_times': all_semester_times,
            # 'current_semester': current_semester,
        }

        return render(request, 'laborganizer/dashboard.html', context)

    # not a POST request, direct to default view
    return redirect('lo_home')


def lo_ta_management(request):
    """TA Management route."""
    context = {}
    # check for post request
    if request.method == 'POST':
        # get value from chosen semester form
        post_semester = request.POST.get('chosen_semester')

        # split results
        semester = {'year': post_semester[3:], 'time': post_semester[:3]}

        # get all TA's assigned to that semester
        tas = get_tas_by_semester(semester['time'], semester['year'])

        # populate context
        context = {
            'tas': tas,
            'semester': semester,
        }

    # always populate semester selection options
    semester_options = Semester.objects.all()
    context['semester_options'] = semester_options

    return render(request, 'laborganizer/ta_management/ta_management.html',
                  context)


def lo_semester_management(request):
    """View for semester information."""
    semesters = Semester.objects.all()

    context = {
        'semesters': semesters,
        }
    return render(request, 'laborganizer/semester_management/semester_management.html',
                  context)


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
