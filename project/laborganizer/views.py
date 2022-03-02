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
from teachingassistant.models import TA, Holds
from .models import Semester, Lab, AllowTAEdit
from optimization.models import TemplateSchedule, TemplateAssignment
from django.contrib import messages
from laborganizer.lo_utils import (get_semester_years,
                                   get_semester_times,
                                   get_current_semester,
                                   get_tas_by_semester,
                                   get_labs_by_semester,
                                   get_most_recent_sched,
                                   get_all_schedule_version_numbers,
                                   get_template_schedule)


def lo_home(request, selected_semester=None, template_schedule=None):
    """
    Home route for the Lab Organizer dashboard.

    Displays data relevant to the active semester based on the time of year.
    """
    if selected_semester is None:
        # establish current semester time/year, based on time
        current_semester = get_current_semester()

    else:
        # get the current semester argument
        current_semester = selected_semester

    # check if a template schedule was given
    if template_schedule is None:
        # if not, get the most recent version of the current semester
        template_schedule = get_most_recent_sched(current_semester['time'],
                                                  current_semester['year'])
    else:
        # use the provided template schedule
        template_schedule = template_schedule

    # get all labs for the current semester
    labs = Lab.objects.filter(
        semester__semester_time=current_semester['time'],
        semester__year=current_semester['year']
    )

    # get all TA's assigned to that semester
    tas = get_tas_by_semester(current_semester['time'],
                              current_semester['year'])

    # get the names of all the semesters for selection purposes
    semester_options = Semester.objects.all()

    # get all template schedule version numbers for selection
    template_schedule_versions = get_all_schedule_version_numbers(
        current_semester['time'],
        current_semester['year'])

    # instantiate context variable
    context = {
        'labs': labs,
        'tas': tas,
        'semester_options': semester_options,
        'current_semester': current_semester,
        'template_schedule': template_schedule,
        'schedule_versions': template_schedule_versions,
    }

    # check if there are no labs in the selected semester
    if len(labs) == 0:
        messages.warning(request, 'No labs in the current semester!')

    return render(request, 'laborganizer/dashboard.html', context)


def lo_select_schedule_version(request):
    """Select a new version of a template schedule to display."""
    if request.method == 'POST':
        version_number = request.POST.get('version_number')
        year = request.POST.get('semester_year')
        time = request.POST.get('semester_time')

        # get that schedule version
        template_schedule = get_template_schedule(time, year, version_number)
        return lo_home(request, None, template_schedule)

    return redirect('lo_home')


def lo_assign_to_template(request):
    """Assign the given TA to the given Lab in the template schedule."""
    if request.method == 'GET':
        # gather data from GET request
        student_id = request.GET.get('student_id')
        course_id = request.GET.get('course_id')
        time = request.GET.get('time')  # time of the desired semester
        year = request.GET.get('year')  # year of the desired semester
        version = request.GET.get('version')  # template schedule version

        # get objects from database
        ta = TA.objects.get(student_id=student_id)
        lab = Lab.objects.get(course_id=course_id)
        template_schedule = get_template_schedule(time, year, version)

        # assign the ta to the selected lab
        template_schedule.assign(ta, lab)
        template_schedule.save()

    return redirect('lo_home')


def lo_select_semester(request):
    """
    View to generate semester information regarding a chosen semester.

    When the LO selects a semester from the lefthand dropdown menu, display
    that semester information.
    """
    if request.method == 'POST':
        semester = request.POST.get('selected_semester')
        year = semester[3:]
        time = semester[:3]
        print(year, time)
        selected_semester = {
            'time': time,
            'year': year,
        }

        # pass the selected semester to the primary view
        return lo_home(request, selected_semester, None)

    return redirect('lo_home')


def lo_generate_schedule(request):
    """View for generating TA schedule via LO command, from the TA Selector."""
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

        # check if the user selected a semester before submitting it
        if post_semester is None:
            messages.warning(request, 'Please select a semester first!')
            return redirect('lo_ta_management')

        # split results
        semester = {'year': post_semester[3:], 'time': post_semester[:3]}

        # get all TA's assigned to that semester
        tas = get_tas_by_semester(semester['time'], semester['year'])

        # get all Hold objects by the current ta's
        holds = []
        for ta in tas:
            hold = Holds.objects.filter(ta=ta)
            if hold is not None:
                holds.append(hold)

        # populate context
        context = {
            'tas': tas,
            'holds': holds,
            'semester': semester,
        }

    # always populate semester selection options
    semester_options = Semester.objects.all()
    context['semester_options'] = semester_options

    return render(request, 'laborganizer/ta_management/ta_management.html',
                  context)


def lo_semester_management(request, selected_semester=None):
    """View for semester information."""
    context = {}
    if request.method == 'POST':

        if selected_semester is None:
            post_semester = request.POST.get('chosen_semester')
        else:
            post_semester = selected_semester

        # check the the user selected a semester before submitting it
        if post_semester is None:
            messages.warning(request, 'Please select a semester first!')
            return redirect('lo_semester_management')

        # split results
        semester = {'year': post_semester[3:], 'time': post_semester[:3]}

        # get all labs assigned to the chosen semester
        labs = get_labs_by_semester(semester['time'], semester['year'])

        # instantiate context variable
        context = {
            'labs': labs,
            'semester': semester,
        }

    # always load options
    semester_options = Semester.objects.all()
    context['semester_options'] = semester_options

    return render(request, 'laborganizer/semester_management/semester_management.html',
                  context)


def lo_edit_lab(request):
    """Update lab information for a single lab."""
    if request.method == 'POST':
        # get all data from the post request
        new_course_id = request.POST.get('course_id')
        new_section = request.POST.get('section')
        new_facility_building = request.POST.get('facility_building')
        new_facility_id = request.POST.get('facility_id')
        new_instructor = request.POST.get('instructor')
        new_days = request.POST.getlist('days[]')
        new_start_time = request.POST.get('start_time')
        new_end_time = request.POST.get('end_time')

        # get the name of the lab from the submit button
        submit_value = request.POST.get('submit')

        print(submit_value)

        # get the previous course ID for database lookup
        old_course_id = request.POST.get('old_course_id')

        # get the lab that needs to be updated
        lab = Lab.objects.get(course_id=old_course_id)

        # update to new information
        lab.course_id = new_course_id
        lab.section = new_section
        lab.set_days(new_days)
        lab.facility_id = new_facility_id
        lab.facility_building = new_facility_building
        lab.instructor = new_instructor
        lab.start_time = new_start_time
        lab.end_time = new_end_time

        # save changes to database
        lab.save()

    return lo_semester_management(request, submit_value)


def lo_allow_ta_edit(request):
    """Allow TA's to edit their information form for the requested time."""
    if request.method == 'POST':
        date = request.POST.get('date')
        time = request.POST.get('time')

        if date != '' or time != '':
            allow_edits = AllowTAEdit.objects.get(pk=1)
            allow_edits.date = date
            allow_edits.time = time
            allow_edits.allowed = True
            allow_edits.save()
            messages.success(request, 'TA\'s are allowed to edit their information!')
        else:
            messages.warning(request, 'Please select a date and a time!')
    return redirect('lo_ta_management')


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
