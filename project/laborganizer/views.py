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
from teachingassistant.models import TA, Holds
from .models import Semester, Lab, AllowTAEdit
from django.contrib import messages
from laborganizer.lo_utils import (get_semester_years,
                                   get_semester_times,
                                   get_current_semester,
                                   get_tas_by_semester,
                                   get_labs_by_semester,
                                   get_most_recent_sched,
                                   get_all_schedule_version_numbers,
                                   get_template_schedule)
from optimization.optimization_utils import (generate_by_selection,
                                             propogate_schedule)
from django.http import JsonResponse
import json


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

    # Handles get request required for generating switches
    if request.GET.get('lab_name') is not None:
        catalog_id = request.GET.get('lab_name')
        response = lo_generate_switches(catalog_id, current_semester)
        return JsonResponse(response, status=200)

    # Handles get request required for confirming switches
    if request.GET.get('swap') is not None:
        switch_data = request.GET.get('swap').split()
        switch_data.pop(0)
        lo_confirm_switch(switch_data)
        messages.success(request, "Switch confirmed!")

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

    # get all history nodes that are active
    last_history = History.objects.last()

    # instantiate context variable
    context = {
        'labs': labs,
        'tas': tas,
        'semester_options': semester_options,
        'current_semester': current_semester,
        'template_schedule': template_schedule,
        'schedule_versions': template_schedule_versions,
        'history': last_history
    }

    # check if there are no labs in the selected semester
    if len(labs) == 0:
        messages.warning(request, 'No labs in the current semester!')

    return render(request, 'laborganizer/dashboard.html', context)


def lo_generate_switches(catalog_id, current_semester):

    # NOTE This version of the function assumes that all Labs are assigned a TA
    # In the future, we will want to implement a dummy TA so that there are no None Types in the database

    contender_number = 3 #TODO make this a global variable

    # Initialize:
    # - General TA List
    # - The top contenders for the switch
    # - The potential scores for labs the current TA could switch to
    # - Current lab
    ta_list, top_contenders = [], []
    relevant_lab_scores = {}
    curr_semester = current_semester # If I do not have this useless alias, it throws a bug and I do not know why for the life of me
    sem_tuple = (curr_semester["time"], curr_semester["year"])

    # filter possible ta's by the semester selected
    for ta in TA.objects.all():
        is_in_sem = False
        for sem in ta.get_all_assigned_semesters():
            if (sem_tuple[0] == sem[0] and sem_tuple[1] == sem[1]):
                is_in_sem = True
        if is_in_sem:
            ta_list.append(ta)

    # set vars for the objects selected via the switch button
    current_lab = Lab.objects.get(catalog_id=catalog_id)
    current_ta = None
    for ta in ta_list:
        if ta.get_all_assigned_labs()[2:5] == catalog_id:
            current_ta = ta
    current_score = current_ta.scores.get(score_catalog_id=catalog_id).score
    ta_list.remove(current_ta)

    # This will sort the TA's from highest to lowest score for this specific lab then take the top 3
    ta_list.sort(key=lambda x: x.scores.get(score_catalog_id=catalog_id).score, reverse=True)
    top_contenders = ta_list[:contender_number]


    # Generate the score table for the current TA, and how the TA would potentially fit into the contenders' labs
    # If it is none, then fill it with dummy data again
    for ta in top_contenders:
        lab_key = ta.get_all_assigned_labs()[2:5]
        if lab_key != "":
            lab_score = current_ta.scores.get(score_catalog_id=lab_key).score
        else:
            lab_score = 0
        relevant_lab_scores[lab_key] = lab_score

    # # Generate the necessary switches, and check if a three-way switch is necessary
    # for catalog_id in relevant_lab_scores:
    #     if relevant_lab_scores[catalog_id] < 0 and current_ta is not None:
    #         switch_possible, best_contender, best_contender_lab = \
    #             generate_three_way_switch(catalog_id, current_ta, lab.catalog_id)
    #         if switch_possible:

    switch_names, switches = [], []
    index = 0

    for ta1 in top_contenders:
        lab1_key = current_lab.catalog_id
        lab2_key = ta1.get_all_assigned_labs()[2:5]
        ta2 = current_ta

        # TODO These scores must be queried relative to the current schedule template
        score1 = ta.scores.get(score_catalog_id=current_lab.catalog_id).score
        score2 = relevant_lab_scores[lab2_key]
        section1 = current_lab.section
        if lab2_key == "":
            section2 = None
        else:
            lab2_obj = Lab.objects.get(catalog_id=lab2_key)
            section2 = lab2_obj.section

        switches.append({"lab1": "CS" + lab1_key,
                         "lab2": "CS" + lab2_key,
                          "TA1": ta1.first_name,
                          "TA2": ta2.first_name,
                       "score1": score1,
                         "score2": relevant_lab_scores[lab2_key],
                         "section1": current_lab.section,
                         "section2": lab2_obj.section})

        switch_names.append("switch_" + str(index + 1))

        index += 1

    response = dict(zip(switch_names, switches))
    print(json.dumps(response, sort_keys=False, indent=4))

    return response

def lo_confirm_switch(switch_data):

    # Prepare data for the switch to occur
    switch_dict = {
        "TA1": switch_data[0],
        "TA2": switch_data[4],
        "Lab1": switch_data[1][3:6],
        "Lab2": switch_data[5][3:6]
    }

    first_lab = Lab.objects.get(catalog_id=switch_dict["Lab1"])
    second_lab = Lab.objects.get(catalog_id=switch_dict["Lab2"])

    # TODO These must be assigned via the templates
    # first_ta = first_lab.assigned_ta
    # second_ta = second_lab.assigned_ta

    node_id = len(History.objects.all()) + 1

    node = History(id=node_id)
    node.save()
    node.ta_1.set([first_ta])
    node.ta_2.set([second_ta])
    node.lab_1.set([first_lab])
    node.lab_2.set([second_lab])
    node.save()

    if (len(History.objects.all()) > 10):
        History.objects.first().delete()

    # Confirm the switch on the database side
    first_lab.confirm_switch(second_lab, first_ta, second_ta)

def lo_select_schedule_version(request):
    """Select a new version of a template schedule to display."""
    if request.method == 'POST':
        version_number = request.POST.get('version_number')
        year = request.POST.get('semester_year')
        time = request.POST.get('semester_time')

        selected_semester = {
            'time': time,
            'year': year
        }

        # get that schedule version
        template_schedule = get_template_schedule(time, year, version_number)
        return lo_home(request, selected_semester, template_schedule)

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

        selected_semester = {
            'time': time,
            'year': year,
        }

        # pass the selected semester to the primary view
        return lo_home(request, selected_semester, None)

    return redirect('lo_home')


def lo_generate_schedule(request):
    """
    View for generating TA schedule via LO command, from the TA Selector.

    Generate a new version of a TemplateSchedule object.
    """
    if request.method == 'POST':
        # get the student id's of all selected TA's
        ta_ids = request.POST.getlist('checks[]')
        year = request.POST.get('year')
        time = request.POST.get('time')

        selected_semester = {
            'time': time,
            'year': year
        }

        # gather a list of all selected TA's
        tas = []
        for ta_id in ta_ids:
            tas.append(TA.objects.get(student_id=ta_id))

        # gather all labs for the selected semester
        labs = get_labs_by_semester(selected_semester['time'],
                                    selected_semester['year'])

        # using those TA's, populate a TemplateSchedule object from
        # optimization.models
        template_schedule = generate_by_selection(tas, labs, selected_semester)

        return lo_home(request, selected_semester, template_schedule)

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


def lo_propogate_schedule(request):
    """Propogate the desired template schedule to the live version."""
    if request.method == 'POST':
        year = request.POST.get('year')
        time = request.POST.get('time')
        version = request.POST.get('version')

        template_schedule = get_template_schedule(time, year, version)
        # import optimization utils and use that propogate_schedule function

        messages.success(request, f'Successfully uploaded version {version}!')
        return redirect('lo_home')
    messages.warning(request, f'Failed to upload version {version}')
    return redirect('lo_home')


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
