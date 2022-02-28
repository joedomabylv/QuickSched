"""Utility functions used in Lab Organizer views."""
from .models import Semester, Lab
from datetime import datetime
from teachingassistant.models import TA


def get_semester_years():
    """
    Get a list of all existing semester years with no duplicates.

    When the LO goes to select a new semester from the sidebar, only display
    each available year (2022, 2023, etc.) once.
    """
    semesters = Semester.objects.all()
    year_list = []
    for semester in semesters:
        if semester.year not in year_list:
            year_list.append(semester.year)
    return year_list


def get_semester_times():
    """
    Get a list of all existing semester times with no duplicates.

    When the LO goes to select a new semester from the sidebar, only display
    each available time (SPR, WNT, etc.) once.
    """
    semesters = Semester.objects.all()
    time_list = []
    for semester in semesters:
        if semester.semester_time not in time_list:
            time_list.append(semester.semester_time)
    return time_list


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
