"""Utility functions used in Lab Organizer views."""
from .models import Semester
from datetime import datetime


def get_semester_years():
    """Get a list of all existing semester years with no duplicates."""
    semesters = Semester.objects.all()
    year_list = []
    for semester in semesters:
        if semester.year not in year_list:
            year_list.append(semester.year)
    return year_list


def get_semester_times():
    """Get a list of all existing semester times with no duplicates."""
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
    return (semester_time, current_year)
