"""Utility functions for the greater optimization functionality."""
from laborganizer.models import Semester
from .models import TemplateSchedule
from laborganizer.lo_utils import (get_most_recent_sched)


def generate_by_selection(tas, labs, semester, priority_bonus=0):
    """
    Generate a template schedule based on LO TA selection.

    tas = Python list
    labs = QuerySet
    """
    # get the most recent semester template schedule and increment the
    # version number by one for the new template schedule
    new_version = get_most_recent_sched(semester['time'],
                                        semester['year']).version_number + 1

    print(semester['time'], semester['year'])

    semester = Semester.objects.get(semester_time=semester['time'],
                                    year=semester['year'])

    # create a new template schedule object with the new version number
    # for the selected semester
    new_template_schedule = TemplateSchedule.objects.create(
        version_number=new_version,
        semester=semester)

    # assign scores to all given TA's for given Labs
    new_template_schedule.initialize(tas, labs, priority_bonus)

    # save new template to databse
    new_template_schedule.save()


def propogate_schedule(template_schedule):
    """Propogate the TemplateSchedule object to the live schedule."""
    pass
