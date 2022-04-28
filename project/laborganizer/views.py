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
from django.core.cache import cache
from teachingassistant.models import TA, Holds
from .models import Semester, Lab, AllowTAEdit, LOCache
from optimization.models import History, TemplateSchedule, TemplateAssignment
from django.contrib import messages
from laborganizer.lo_utils import (get_current_semester,
                                   get_tas_by_semester,
                                   get_labs_by_semester,
                                   get_most_recent_sched,
                                   get_all_schedule_version_numbers,
                                   get_template_schedule,
                                   get_deviation_score,
                                   grade_deviation_score,
                                   semester_exists,
                                   generate_semester_dictionary,
                                   get_semester_cluster,
                                   parse_semester_lab_dict,
                                   validate_course_id,
                                   validate_edit_course_id,
                                   filter_out_unscored,
                                   filter_out_nolabs,
                                   add_labs)
from django.contrib.auth.decorators import login_required
from optimization.optimization_utils import (generate_by_selection,
                                             propogate_schedule)
from django.http import JsonResponse


@login_required
def lo_home(request, selected_semester=None, template_schedule=None):
    """
    Home route for the Lab Organizer dashboard.

    Displays data relevant to the active semester based on the time of year.
    """
    # ensure the user is a superuser
    if request.user.is_superuser:
        context = {}
        # get the LO Cache
        lo_cache = LOCache.objects.all().first()
        if Semester.objects.all().exists():
            if lo_cache.get_semester() is None:
                # establish current semester time/year, based on time
                current_semester = cache.get('most_recent_semester')
                if current_semester is None:
                    current_semester = get_current_semester()

            else:
                # get the current semester argument
                current_semester = lo_cache.get_semester()
                lo_cache.set_semester(current_semester)

            # check if a template schedule was given
            if lo_cache.get_template_schedule() is None:
                # if not, get the most recent version of the current semester
                template_schedule = get_most_recent_sched(current_semester['time'],
                                                          current_semester['year'])
            else:
                # use the provided template schedule, if it exists for the
                # cached semester
                template_schedule = lo_cache.get_template_schedule()
                if not lo_cache.template_exists(template_schedule):
                    template_schedule = get_most_recent_sched(current_semester['time'],
                                                              current_semester['year'])

            # Handles get request required for generating switches
            if request.GET.get('lab_name') is not None:
                catalog_id = request.GET.get('lab_name')
                response = lo_generate_switches(catalog_id,
                                                current_semester,
                                                template_schedule)
                return JsonResponse(response, status=200)

            # Handles get request required for undoing changes
            if request.GET.get('undo') is not None:
                node = template_schedule.his_nodes.last()
                if node is not None:
                    if not node.is_assignment:
                        to_assignment, from_assignment = None, None
                        for assignment in template_schedule.assignments.all():
                            if assignment.ta == node.ta_1.first():
                                from_assignment = assignment
                            elif assignment.ta == node.ta_2.first():
                                to_assignment = assignment

                        node.undo_bilateral_switch(template_schedule, from_assignment, to_assignment)
                    else:
                        template_schedule.assign(node.ta_1.first(), node.lab_1.first())
                    node.delete()

            # Handles get request required for confirming switches
            if request.GET.get('swap') is not None:
                switch_data = request.GET.get('swap').split()
                switch_data.pop(0)
                lo_confirm_switch(switch_data, template_schedule)
                messages.success(request, "Switch confirmed!")

            # get all labs for the current semester
            labs = Lab.objects.filter(
                semester__semester_time=current_semester['time'],
                semester__year=current_semester['year']
            )

            # get all TA's assigned to that semester
            tas = get_tas_by_semester(current_semester['time'],
                                      current_semester['year'])

            # check if there are any TA's with incomplete profiles
            ta_incomplete = False
            for ta in tas:
                hold = Holds.objects.get(ta=ta)
                if hold.incomplete_profile:
                    ta_incomplete = True

            # get the names of all the semesters for selection purposes
            semester_options = Semester.objects.all()

            # get all template schedule version numbers for selection
            template_schedule_versions = get_all_schedule_version_numbers(
                current_semester['time'],
                current_semester['year'])

            # get all history nodes that are active
            history = template_schedule.his_nodes.all()

            # instantiate context variable
            context = {
                'labs': labs,
                'tas': tas,
                'semester_options': semester_options,
                'current_semester': current_semester,
                'template_schedule': template_schedule,
                'schedule_versions': template_schedule_versions,
                'history': history,
                'ta_incomplete': ta_incomplete,
            }

        return render(request, 'laborganizer/dashboard.html', context)

    # user it not a superuser, take them to the login back
    return redirect('sign_in')


@login_required
def lo_flip_contract_status(request):
    """Flip the contracted status of a TA."""
    if request.method == 'POST':
        ta = TA.objects.get(student_id=request.POST.get('ta_id'))
        ta.flip_contract_status()
        return JsonResponse({'result': True}, status=200)
    else:
        messages.error(request, 'Could not update contract status')
        return JsonResponse({'result': False}, status=200)


def lo_generate_switches(course_id, current_semester, template_schedule):
    """Generate all available switches for a lab at LO command."""
    contender_number = 5  # TODO make this a global variable

    # initialize variables
    top_contenders = []
    relevant_lab_scores = {}

    # gather all TA's based on the currently selected semester
    tas = get_tas_by_semester(current_semester['time'],
                              current_semester['year'])

    # get the selected lab based on course ID
    selected_lab = Lab.objects.get(course_id=course_id)
    selected_ta = None
    for assignment in template_schedule.assignments.all():
        if assignment.lab.course_id == course_id:
            selected_ta = assignment.ta

    if selected_ta is not None:
        current_score = selected_ta.get_score(selected_lab, template_schedule.id)
    else:
        return None

    # remove selected ta so that it is not compared against itself
    tas = list(tas)
    tas.remove(selected_ta)

    # remove TA's that were not considered for scoreing
    tas = filter_out_unscored(tas)

    # filter out tas with no previous lab assignments
    tas = filter_out_nolabs(tas, template_schedule)

    # calculate the deviation score for each relevant TA
    deviation_scores = []
    for ta in tas:
        st_score, pt_score, score = get_deviation_score(ta, selected_ta, selected_lab,
                                                current_score, template_schedule)
        deviation_scores.append((score, ta.student_id, st_score, pt_score))

    # sort the list of TA's based on their deviation score instead of their fitness score
    deviation_scores.sort(key=lambda x: x[0])

    # Take the top N scores with their respective student ids
    top_contenders = deviation_scores[0:contender_number]

    switch_names = []
    switches = []
    index = 0

    # determine which TA's we can switch the selected TA to
    for ta in top_contenders:

        # find ta object with student id
        to_ta = TA.objects.get(student_id=ta[1])

        # find grade of deviation score
        grade = grade_deviation_score(ta[0])

        # possible labs we're switching to based on the current template
        to_labs = to_ta.get_assignments_from_template(template_schedule)

        # check for one lab we could switch into
        to_lab = to_labs[0]

        switches.append({
            "to_lab": to_lab.subject + to_lab.catalog_id + ':' + to_lab.course_id,
            "from_lab": selected_lab.subject + selected_lab.catalog_id + ':' + selected_lab.course_id,
            "to_ta": to_ta.first_name + ":" + to_ta.student_id,
            "from_ta": selected_ta.first_name + ":" + selected_ta.student_id,
            "deviation_score": ta[0],
            "score_color": grade,
            "switch_id": index + 1,
            "st_score": ta[2],
            "pt_score": ta[3]
        })

        switch_names.append("switch_" + str(index + 1))

        index += 1

    response = dict(zip(switch_names, switches))
    return response


def lo_confirm_switch(switch_data, template_schedule):
    """Confirm a switch within the database according to the template."""
    # Prepare data for the switch to occur
    switch_dict = {
        "first_ta": switch_data[0],  # format <first_name>:<student_id>
        "first_course": switch_data[1],  # format: <subject><catalog_id>:<course_id>
        "second_ta": switch_data[5],  # format <first_name>:<student_id>
        "second_course": switch_data[6]  # format: <subject><catalog_id>:<course_id>
    }

    # extract the student ID from the desired TA's
    first_student_id = switch_dict['first_ta'].split(':')[1]
    second_student_id = switch_dict['second_ta'].split(':')[1]

    # get the desired TA's based on their student ID
    from_ta = TA.objects.get(student_id=first_student_id)
    to_ta = TA.objects.get(student_id=second_student_id)

    # extract the course ID from the desired labs
    first_course_id = switch_dict['first_course'].split(':')[1].replace(')', '')
    second_course_id = switch_dict['second_course'].split(':')[1].replace(')', '')

    # get the desired lab assignments from the template schedule
    from_assignment = template_schedule.get_assignment_from_id(first_course_id)
    to_assignment = template_schedule.get_assignment_from_id(second_course_id)

    # get the desired labs based on course ID
    from_lab = Lab.objects.get(course_id=first_course_id)
    to_lab = Lab.objects.get(course_id=second_course_id)

    relative_node_id = len(template_schedule.his_nodes.all()) + 1
    abs_node_id = len(History.objects.all()) + 1

    node = History(id=abs_node_id)
    node.save()
    node.relative_node_id = relative_node_id
    node.ta_1.set([from_ta])
    node.ta_2.set([to_ta])
    node.lab_1.set([from_lab])
    node.lab_2.set([to_lab])
    node.temp_sched = template_schedule
    node.save()

    if (len(template_schedule.his_nodes.all()) > 10):
        template_schedule.his_nodes.first().delete()

    # Confirm the switch on the database side
    template_schedule.swap_assignments(from_assignment, to_assignment)

    return redirect('lo_home')

def generate_assignment_node(ta, lab, template_schedule):
    """Generate an assignment history node for record"""

    # find idenity of other TA to switch
    other_ta = None
    for assignment in TemplateAssignment.objects.all():
        if assignment.lab == lab:
            other_ta = assignment.ta

    # set up node for switching
    relative_node_id = len(template_schedule.his_nodes.all()) + 1
    abs_node_id = len(History.objects.all()) + 1

    # create said node
    node = History(id=abs_node_id)
    node.save()
    node.relative_node_id = relative_node_id
    node.ta_1.set([other_ta])
    node.ta_2.set([ta])
    node.lab_1.set([lab])
    node.lab_2.set([None])
    node.temp_sched = template_schedule
    node.is_assignment = True
    node.save()


@login_required
def lo_select_schedule_version(request):
    """Select a new version of a template schedule to display."""
    # get the lo cache
    lo_cache = LOCache.objects.all().first()
    # ensure the user is a superuser
    if request.user.is_superuser:
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

            lo_cache.set_semester(selected_semester)
            lo_cache.set_template_schedule(template_schedule)

        return redirect('lo_home')

    # user is not a superuser, take them back to the login page
    return redirect('sign_in')


@login_required
def lo_assign_to_template(request):
    """Assign the given TA to the given Lab in the template schedule."""
    # ensure the user is a superuser
    if request.user.is_superuser:
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

            # generate the history node for the assignment
            generate_assignment_node(ta, lab, template_schedule)

            # assign the ta to the selected lab
            template_schedule.assign(ta, lab)
            template_schedule.save()

        return redirect('lo_home')

    # user is not a superuser, take them back to the login page
    return redirect('sign_in')


@login_required
def lo_select_semester(request):
    """
    View to generate semester information regarding a chosen semester.

    When the LO selects a semester from the lefthand dropdown menu, display
    that semester information.
    """
    # get the lo cache
    lo_cache = LOCache.objects.all().first()
    # ensure the user is a superuser
    if request.user.is_superuser:
        if request.method == 'POST':
            semester = request.POST.get('selected_semester')
            year = semester[3:]
            time = semester[:3]

            selected_semester = {
                'time': time,
                'year': year,
            }

            # set the cache for selection in lo_home
            lo_cache.set_semester(selected_semester)

        return redirect('lo_home')

    # the user is not a superuser, take them back to the login page
    return redirect('sign_in')


@login_required
def lo_generate_schedule(request):
    """
    View for generating TA schedule via LO command, from the TA Selector.

    Generate a new version of a TemplateSchedule object.
    """
    # get the lo cache
    lo_cache = LOCache.objects.all().first()
    # ensure the user is a superuser
    if request.user.is_superuser:
        if request.method == 'POST':

            # NOTE The priority bonus is subject to change in further iterations
            # I didnt hardcode the values in the html so they could be easily changed here
            priority_value_table = {
                'none': 0,
                'low': 10,
                'high': 20
            }

            priority = request.POST.get('priority')
            priority_bonus = priority_value_table[priority]

            # get the student id's of all selected TA's
            ta_ids = request.POST.getlist('checks[]')
            year = request.POST.get('year')
            time = request.POST.get('time')

            selected_semester = {
                'time': time,
                'year': year
            }

            # gather a list of all selected TA's, if any
            if len(ta_ids) != 0:
                tas = []
                for ta_id in ta_ids:
                    ta = TA.objects.get(student_id=ta_id)
                    tas.append(ta)
            else:
                # there are no selected TA's, we cannot create a schedule
                messages.warning(request, 'There are no TA\'s selected to generate a schedule for!')
                return redirect('lo_home')

            # gather all labs for the selected semester
            labs = get_labs_by_semester(selected_semester['time'],
                                        selected_semester['year'])

            # check if there are any labs in the chosen semester
            if labs is not None:
                # using those TA's, populate a TemplateSchedule object from
                # optimization.models
                template_schedule = generate_by_selection(tas, labs, selected_semester, priority_bonus)

                # set the cache
                lo_cache.set_semester(selected_semester)
                lo_cache.set_template_schedule(template_schedule)

                return redirect('lo_home')

            # there are no labs in the semester, warn the user
            messages.warning(request, "Please create labs before creating a schedule!")
            # cache the selected semester
            lo_cache.set_semester(selected_semester)
            return redirect('lo_home')

        # not a POST request, direct to default view
        return redirect('lo_home')

    # user is not a superuser, take them back to the login page
    return redirect('sign_in')


@login_required
def lo_ta_management(request):
    """TA Management route."""
    # ensure the user is a superuser
    if request.user.is_superuser:
        context = {}
        # get all TA objects
        tas = TA.objects.all()

        # get all holds objects applied to those TA's
        holds = []
        for ta in tas:
            hold = Holds.objects.filter(ta=ta)
            if hold is not None:
                holds.append(hold)

        # check if there are any TA's in the system that have not provided
        # initial data
        uninitialized_tas = False
        for ta in tas:
            if ta.student_id is None:
                uninitialized_tas = True

        # get all semester objects
        current_semester = get_current_semester()
        all_semesters = get_semester_cluster(current_semester)
        allow_edit = AllowTAEdit.objects.all()[0].allowed

        # generate context variable
        context = {
            'tas': tas,
            'holds': holds,
            'all_semesters': all_semesters,
            'allowed_edit': allow_edit,
            'current_semester': current_semester,
            'uninitialized_tas': uninitialized_tas,
        }

        # always populate semester selection options
        semester_options = Semester.objects.all()
        context['semester_options'] = semester_options

        return render(request, 'laborganizer/ta_management/ta_management.html',
                      context)

    # user is not a superuser, take them back to the login page
    return redirect('sign_in')


@login_required
def lo_update_ta_semesters(request):
    """Update TA assigned semesters."""
    # ensure the user is a superuser
    if request.user.is_superuser:
        if request.method == 'POST':
            selected_semesters = request.POST.getlist('selected_semesters[]')
            if not selected_semesters:
                messages.warning(request, 'Please choose semesters to update! If there are none, add some from the Semester Management tab!')
                return redirect('lo_ta_management')
            ta = TA.objects.get(student_id=request.POST.get('submit'))
            ta.update_semesters(selected_semesters)
            messages.success(request, 'Updated semester assignments!')
        return redirect('lo_ta_management')

    # user is not a superuser, take them back to the login page
    return redirect('sign_in')


@login_required
def lo_semester_management(request, selected_semester=None):
    """View for semester information."""
    # ensure the user is a superuser
    if request.user.is_superuser:
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

    # user is not a superuser, take them back to the login page
    return redirect('sign_in')


@login_required
def lo_propogate_schedule(request):
    """Propogate the desired template schedule to the live version."""
    # get the lo cache
    lo_cache = LOCache.objects.all().first()
    # ensure the user is a superuser
    if request.user.is_superuser:
        if request.method == 'POST':
            year = request.POST.get('year')
            time = request.POST.get('time')
            version = request.POST.get('version')

            if not version:
                messages.warning(request, 'There is no template schedule to propogate!')
                return redirect('lo_home')

            labs = get_labs_by_semester(time, year)

            # check if there are any labs assigned to this semester
            if labs is not None:
                # get all TA's assigned to this semester
                all_tas = get_tas_by_semester(time, year)

                # get the template schedule object
                schedule = get_template_schedule(time, year, version)

                # check if there is at least one TA assigned to a lab in this
                # template schedule
                if not schedule.has_one_assignment():
                    messages.warning(request, 'There needs to be at least one TA assigned to a lab in order to propogate!')
                    return redirect('lo_home')

                # propogate the schedule to the live version
                propogate_schedule(schedule, all_tas)

                selected_semester = {
                    'time': time,
                    'year': year
                }

                messages.success(request, f'Successfully uploaded version {version}!')
                lo_cache.set_semester(selected_semester)
                lo_cache.set_template_schedule(schedule)
                return redirect('lo_home')

        # there are no labs, warn the user
        messages.warning(request, 'There are no labs to propogate a schedule for!')
        return redirect('lo_home')

    # user is not a superuser, take them back to the login page
    return redirect('sign_in')


@login_required
def lo_edit_lab(request):
    """Update lab information for a single lab."""
    # ensure the user is a superuser
    if request.user.is_superuser:
        if request.method == 'POST':
            # get the previous course ID for database lookup and validation
            old_course_id = request.POST.get('old_course_id')

            # get all data from the post request
            new_course_id = validate_edit_course_id(request.POST.get('course_id'),
                                                    old_course_id)
            new_section = request.POST.get('section')
            new_facility_building = request.POST.get('facility_building')
            new_facility_id = request.POST.get('facility_id')
            new_instructor = request.POST.get('instructor')
            new_days = request.POST.getlist('days[]')
            new_start_time = request.POST.get('start_time')
            new_end_time = request.POST.get('end_time')

            if not new_course_id[1]:
                messages.warning(request, 'The new course ID you\'ve provided is in use by another course!')
                return redirect('lo_semester_management')

            # get the name of the lab from the submit button
            submit_value = request.POST.get('submit')

            # get the lab that needs to be updated
            try:
                lab = Lab.objects.get(course_id=old_course_id)
            except Lab.DoesNotExist:
                messages.warning(request, 'Something went wrong. Please refresh the page and try again!')
                return redirect('lo_semester_management')

            # update to new information
            lab.course_id = new_course_id[0]
            lab.section = new_section
            lab.set_days(new_days)
            lab.facility_id = new_facility_id
            lab.facility_building = new_facility_building
            lab.instructor = new_instructor
            lab.start_time = new_start_time
            lab.end_time = new_end_time

            # save changes to database
            lab.save()

        messages.success(request, f'Successfully edited {lab}!')
        return lo_semester_management(request, submit_value)

    # user is not a superuser, take them back to the login page
    return redirect('sign_in')


@login_required
def lo_allow_ta_edit(request):
    """Allow TA's to edit their information form for the requested time."""
    if request.user.is_superuser:
        if request.method == 'POST':
            ta = TA.objects.get(student_id=request.POST.get('ta'))
            holds = Holds.objects.get(pk=ta.holds_key)
            holds.incomplete_profile = True
            holds.save()
            messages.success(request, f'{ta} is now allowed to edit their information!')
            return redirect('lo_ta_management')
    # the user is not a superuser, take them back to the login page
    return redirect('sign_in')


@login_required
def lo_new_semester(request):
    """Handle the new semester form submitted by a user."""
    # ensure the user is a superuser
    if request.user.is_superuser:
        if request.method == "POST":
            year = request.POST.get('selected_year')
            time = request.POST.get('selected_time')

            # check if the requested semester already exists
            if semester_exists(year, time):
                messages.warning(request, f'A semester for {time}{year} already exists!')
                return redirect('lo_semester_management')

            # check if a user attached a CSV file to their addition
            if len(request.FILES) != 0:
                semester_csv = request.FILES['semester_csv']
                # check if the file is a CSV file
                if not semester_csv.name.endswith('.csv'):
                    messages.error(request, 'Please upload a CSV file!')
                    return redirect('lo_semester_management')
                return lo_csv_lab_upload(request, semester_csv, time, year)
            # there is no CSV file, create empty semester object and template schedule
            else:
                # create semester object
                semester = Semester.objects.create(semester_time=time, year=year)

                # create template schedule for that semester
                TemplateSchedule.objects.create(version_number=0, semester=semester)

                # inform the user of success
                messages.success(request, f'Added a new semester for {time}{year}!')
        return redirect('lo_semester_management')

    # user is not a superuser, take them back to the login page
    return redirect('sign_in')


@login_required
def lo_csv_lab_upload(request, semester_csv=None, time=None, year=None):
    """Display information to Lab Organizer regarding new Semester CSV."""
    # ensure the user is a superuser
    if request.user.is_superuser:
        semester_data = generate_semester_dictionary(semester_csv, time, year)
        context = {
            'time': time,
            'year': year,
            'semester_data': semester_data,
        }
        return render(request, 'laborganizer/csv_upload/csv_upload.html', context)

    # user is not a superuser, take them back to the login page
    return redirect('sign_in')


@login_required
def lo_csv_lab_upload_confirm(request):
    """After a Lab Organizer has confirmed lab information, update database."""
    # check if the user is a superuser
    if request.user.is_superuser:
        if request.method == 'POST':
            class_names = request.POST.getlist('class_names')
            subjects = request.POST.getlist('subjects')
            catalog_ids = request.POST.getlist('catalog_ids')
            course_ids = request.POST.getlist('course_ids')
            sections = request.POST.getlist('sections')
            days = request.POST.getlist('days')
            facility_ids = request.POST.getlist('facility_ids')
            facility_buildings = request.POST.getlist('facility_buildings')
            instructors = request.POST.getlist('instructors')
            start_times = request.POST.getlist('start_times')
            end_times = request.POST.getlist('end_times')

            total_class_number = request.POST.get('number_of_labs')
            time = request.POST.get('semester_time')
            year = request.POST.get('semester_year')

            lab_dict = {
                'class_names': class_names,
                'subjects': subjects,
                'catalog_ids': catalog_ids,
                'course_ids': course_ids,
                'sections': sections,
                'days': days,
                'facility_ids': facility_ids,
                'facility_buildings': facility_buildings,
                'instructors': instructors,
                'start_times': start_times,
                'end_times': end_times,
            }

            lab_list = parse_semester_lab_dict(lab_dict, total_class_number)

            # create a new semester object
            new_semester = Semester.objects.create(semester_time=time, year=year)

            # create new template schedule
            TemplateSchedule.objects.create(version_number=0, semester=new_semester)

            result = add_labs(lab_list, new_semester)

            if result:
                messages.success(request, f'Successfully created {new_semester}!')
            else:
                messages.error(request, 'Could not create a new semester')
        return redirect('lo_semester_management')

    # user is not a superuser, take them back to the login page
    return redirect('sign_in')


def lo_new_lab(request):
    """Create a single new lab for a given semester."""
    # ensure the user is a superuser
    if request.user.is_superuser:

        semester_options = Semester.objects.all()

        if semester_options:
            context = {
                'semester_options': semester_options,
            }
            return render(request, 'laborganizer/semester_management/new_lab.html',
                          context)
        messages.warning(request, 'There are no semesters to add a lab to!')
        return redirect('lo_semester_management')

    # user is not a superuser, take them back to the login page
    return redirect('sign_in')


def lo_new_lab_confirm(request):
    """Confirm the addition of a new lab and add it to the database."""
    # ensure the user is a superuser
    if request.user.is_superuser:
        if request.method == 'POST':
            semester = request.POST.get('semester')
            class_name = request.POST.get('class_name')
            section = request.POST.get('section')
            subject = request.POST.get('subject')
            catalog_id = request.POST.get('catalog_id')
            course_id = validate_course_id(request.POST.get('course_id'))
            instructor = request.POST.get('instructor')
            days = request.POST.getlist('days[]')
            facility_id = request.POST.get('facility_id')
            facility_building = request.POST.get('facility_building')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')

            # check if course ID is valid
            if not course_id[1]:
                messages.warning(request, 'The lab you\'re attempting to create has a course ID in use by another lab!')
                return redirect('lo_semester_management')
				
            # check if start time is after end time
            if start_time >= end_time:
                messages.warning(request, 'The lab you\'re attempting to create has an invalid start and end time!')
                return redirect('lo_semester_management')

            # get the chosen semester object
            semester_time = semester[:3]
            semester_year = semester[3:]
            try:
                semester_object = Semester.objects.get(semester_time=semester_time,
                                                   year=semester_year)
            except Semester.DoesNotExist:
                messages.error(request, 'Something went wrong... the semester you\'ve chosen does not exist!')
                return redirect('lo_semester_management')

            new_lab = Lab.objects.create(
                class_name=class_name,
                section=section,
                subject=subject,
                catalog_id=catalog_id,
                course_id=course_id[0],
                instructor=instructor,
                facility_id=facility_id,
                facility_building=facility_building,
                start_time=start_time,
                end_time=end_time,
                semester=semester_object
            )

            # ensure days follow the proper format of a character
            # separated by a space
            new_lab.set_days(days)
            new_lab.save()

            messages.success(request, f'Successfully created {new_lab}!')
            return redirect('lo_semester_management')
    return redirect('sign_in')


@login_required
def lo_csv_upload_help(request):
    """Display HTML to Lab Organizer informing them how to format a CSV."""
    # ensure the user is a superuser
    if request.user.is_superuser:
        return render(request, 'laborganizer/csv_upload/csv_help.html')

    # user is not a superuser, take them back to the login page
    return redirect('sign_in')


@login_required
def lo_display_semester(request):
    """Display information regarding a single semester."""
    # ensure the user is a superuser
    if request.user.is_superuser:
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

    # user is not a superuser, take them back to the login page
    return redirect('sign_in')


@login_required
def lo_upload(request):
    """View to upload CSV file. Probably going to be deleted, see Andrew."""
    return render(request, 'laborganizer/dashboard.html')
