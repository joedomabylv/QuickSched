"""Utility functions used in Lab Organizer views."""
from .models import Semester, Lab
from datetime import datetime
from teachingassistant.models import TA
from optimization.models import TemplateSchedule
import csv


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


def get_deviation_score(potential_ta, selected_ta, selected_lab, current_score, template_schedule):
    # NOTE This algorithm assumes that the initially generated schedule is the best possible schedule, and
    # anything deviating from such is a downgrade. This function calculates how much the respective
    # scores are straying away from the original scores, and returning that value of gaps.
    # The higher the difference, the worse of a choice it should be.

    pt_labs = potential_ta.get_assignments_from_template(template_schedule)
    pt_potential_score = potential_ta.get_score(selected_lab, template_schedule.id)
    st_current_score = current_score

    # if the potential ta doesnt have an assignment, just return the difference between st and pt scores
    if len(pt_labs) == 0:

        # NOTE temporary bug fix
        if pt_potential_score is None or st_current_score is None:
            return 0, 0, 0

        return abs(pt_potential_score - st_current_score), 0, 0
    else:
        pt_lab = pt_labs[0]
        pt_current_score = potential_ta.get_score(selected_lab, template_schedule.id)
        st_potential_score = selected_ta.get_score(pt_lab, template_schedule.id)

        # NOTE temporary bug fix
        if pt_potential_score is None or st_current_score is None \
           or pt_current_score is None or st_potential_score is None:
            return 0, 0, 0

        gap_1 = abs(st_current_score - st_potential_score)
        gap_2 = abs(pt_current_score - pt_potential_score)

        return gap_1, gap_2, gap_1 + gap_2


def grade_deviation_score(score):
    if score < 20:
        return "score5"
    elif score < 40:
        return "score3"
    elif score < 60:
        return "score4"
    else:
        return "score1"


def semester_exists(year, time):
    """Check if a semester already exists for a given time and year."""
    try:
        Semester.objects.get(semester_time=time, year=year)
        return True
    except Semester.DoesNotExist:
        return False


def lab_exists(course_id):
    """Check if a lab exists for given class name and course ID."""
    try:
        Lab.objects.get(course_id=course_id)
        return True
    except Lab.DoesNotExist:
        return False


def validate_days(days):
    """Ensure a given set of days is properly formatted for the database."""
    valid_days = ['M', 'T', 'W', 'Th', 'F']
    split_days = days.split(' ')
    for day in split_days:
        if day not in valid_days:
            return False
    return True


def validate_time(time):
    """Ensure a given time is properly formatted for the database."""
    try:
        datetime.strptime(time, '%I:%M')
        return True
    except ValueError:
        return False


def add_labs(labs_list, semester):
    """Add labs to the database for prevalidated data to a given semester."""
    # try:
    for lab in labs_list:
        Lab.objects.create(
            class_name=lab['class_name'],
            subject=lab['subject'],
            catalog_id=lab['catalog_id'],
            course_id=lab['course_id'],
            section=lab['section'],
            days=lab['days'],
            facility_id=lab['facility_id'],
            facility_building=lab['facility_building'],
            instructor=lab['instructor'],
            start_time=lab['start_time'],
            end_time=lab['end_time'],
            semester=semester
        )
    # except:
    #     return (False, 'Something went wrong when adding labs!')
    return (True, 'success')


def handle_semester_csv(semester_csv, time, year):
    """
    Handle a given semester CSV file and create a new semester object.

    Return True on success, False on failure.
    """
    rows = semester_csv.read().decode('UTF-8').split('\n')
    data_list = []
    for index, row in enumerate(rows):
        fields = row.split(',')
        field_dict = {}
        # check if there are a valid number of fields
        if len(fields) != 11:
            return (False, f'Row {index + 1} has an incorrect number of fields!')

        field_dict['class_name'] = fields[0]
        field_dict['subject'] = fields[1]
        field_dict['catalog_id'] = fields[2]
        field_dict['course_id'] = fields[3]
        field_dict['section'] = fields[4]
        field_dict['days'] = fields[5]
        field_dict['facility_id'] = fields[6]
        field_dict['facility_building'] = fields[7]
        field_dict['instructor'] = fields[8]
        field_dict['start_time'] = fields[9]
        field_dict['end_time'] = fields[10]

        if not validate_days(field_dict['days']):
            return (False, f'Malformed days in row {index + 1}!')

        if not validate_time(field_dict['start_time']):
            return (False, f'Malformed starting time in row {index + 1}!')

        if not validate_time(field_dict['end_time']):
            return (False, f'Malformed ending time in row {index + 1}!')

        if lab_exists(field_dict['course_id']):
            return (False, f'The lab in row {index + 1} already exists!')

        data_list.append(field_dict)

    # data is prevalidated, create a new semester and add all the labs to it
    semester = Semester.objects.create(semester_time=time, year=year)
    return add_labs(data_list, semester)
