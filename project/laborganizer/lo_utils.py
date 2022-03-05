"""Utility functions used in Lab Organizer views."""
from .models import Semester, Lab
from datetime import datetime
from teachingassistant.models import TA
from optimization.models import TemplateSchedule


# def get_semester_years():
#     """
#     Get a list of all existing semester years with no duplicates.

#     When the LO goes to select a new semester from the sidebar, only display
#     each available year (2022, 2023, etc.) once.
#     """
#     semesters = Semester.objects.all()
#     year_list = []
#     for semester in semesters:
#         if semester.year not in year_list:
#             year_list.append(semester.year)
#     return year_list


# def get_semester_times():
#     """
#     Get a list of all existing semester times with no duplicates.

#     When the LO goes to select a new semester from the sidebar, only display
#     each available time (SPR, WNT, etc.) once.
#     """
#     semesters = Semester.objects.all()
#     time_list = []
#     for semester in semesters:
#         if semester.semester_time not in time_list:
#             time_list.append(semester.semester_time)
#     return time_list


def get_current_semester():
    """Try and guess which semester is currently going on based on the time."""
    current_month = datetime.now().month
    current_year = datetime.now().year
    semester_time = ''
    # between january and may
    if current_month >= 1 and current_month <= 5:
        semester_time = 'SPR'
    # between june and july
    elif current_month > 5 and current_month < 8:
        semester_time = 'SUM'
    # between august and november
    elif current_month >= 8 and current_month <= 11:
        semester_time = 'FAL'
    # december
    else:
        semester_time = 'WNT'

    current_semester_dict = {
        'time': semester_time,
        'year': current_year,
    }

    return current_semester_dict


def get_tas_by_semester(time, year):
    """Get a list of all TA's assigned to the specified semester."""
    tas = TA.objects.filter(assigned_semesters__semester_time=time,
                            assigned_semesters__year=year)
    return tas


def get_labs_by_semester(time, year):
    """Get a list of all Labs assigned to a specific semester."""
    labs = Lab.objects.filter(semester__semester_time=time,
                              semester__year=year)
    return labs


def get_most_recent_sched(time, year):
    """Get the most recent template schedule based on the given semester."""
    # get the semester based on the time and year
    semester = Semester.objects.get(semester_time=time,
                                    year=year)
    # grab all the schedule templates by semester
    template_schedules = TemplateSchedule.objects.filter(semester=semester)

    # find the one with the biggest version number
    largest_version = 0
    for schedule in template_schedules:
        if schedule.version_number > largest_version:
            largest_version = schedule.version_number
    return TemplateSchedule.objects.get(semester=semester,
                                        version_number=largest_version)


def get_all_schedule_version_numbers(time, year):
    """
    Get the version numbers of all template schedules for the semester.

    Based on time and year.
    """
    # get the desired semester
    semester = Semester.objects.get(semester_time=time,
                                    year=year)

    # get all template schedules based on semester
    template_schedules = TemplateSchedule.objects.filter(semester=semester)

    # get the version numbers of all template schedules
    version_list = []
    for schedule in template_schedules:
        version_list.append(schedule.version_number)

    return version_list


def get_template_schedule(time, year, version):
    """Get the template schedule based on semester and version number."""
    # get the semester object
    semester = Semester.objects.get(semester_time=time,
                                    year=year)
    return TemplateSchedule.objects.get(semester=semester,
                                        version_number=version)

def get_max_score(tas, lab, template_schedule):
    """Get the max score for a single lab against a set of TA's."""
    max_score = 0
    for ta in tas:
        current_score = ta.get_score(lab, template_schedule.id)
        if current_score > max_score:
            max_score = current_score
    return max_score


def get_top_scoring_contenders(tas, lab, template_schedule, selected_ta, limit):
    """
    Get the top scores for a template_schedule based on the pper limit.

    Return a list of tuples in the format:
    [(ta, score), (ta, score), ...]
    """
    max_score = get_max_score(tas, lab, template_schedule)
    top_contenders = []
    for ta in tas:
        # check if we've reached the limit of desired contenders
        if len(top_contenders) < limit:
            current_score = ta.get_score(lab, template_schedule.id)
            # check if the scores are equivalent and we're not adding
            # the selected TA to the list
            # (we don't want to compare possible switches with the
            #  same TA)
            if (current_score == max_score and
                ta.student_id != selected_ta.student_id):
                top_contenders.append(ta)
    return top_contenders


def get_top_scoring_labs(tas, template_schedule):
    """Generate a list of all labs that a list of TA's are assigned to."""
    lab_list = []
    for ta in tas:
        assignments = ta.get_assignments_from_template(template_schedule)
        for assignment in assignments:
            if assignment not in lab_list:
                lab_list.append(assignment)
    return lab_list
