"""Utility functions used in Lab Organizer views."""
from .models import Semester, Lab
from datetime import datetime
from teachingassistant.models import TA
from optimization.models import TemplateSchedule
from django.core.exceptions import ObjectDoesNotExist
from io import StringIO
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

    # check if the semester doesn't exist in the database
    # if not, default to the first semester in the database
    if not check_if_sem_exists(current_semester_dict):
        try:
            current_semester_dict['time'] = Semester.objects.all().first().semester_time
            current_semester_dict['year'] = Semester.objects.all().first().year
        except AttributeError:
            current_semester_dict['time'] = ''
            current_semester_dict['year'] = 0

    return current_semester_dict


def get_tas_by_semester(time, year):
    """Get a list of all TA's assigned to the specified semester."""
    tas = TA.objects.filter(assigned_semesters__semester_time=time,
                            assigned_semesters__year=year)
    return tas

def check_if_sem_exists(semester_dict):
    time = semester_dict['time']
    year = semester_dict['year']
    try:
        semester = Semester.objects.get(semester_time=time, year=year)
    except ObjectDoesNotExist:
        return False
    return True

def get_labs_by_semester(time, year):
    """Get a list of all Labs assigned to a specific semester."""
    if time and year:
        try:
            labs = Lab.objects.filter(semester__semester_time=time,
                                   semester__year=year)
            return labs
        except Lab.DoesNotExist:
            return None
    return None


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
        return abs(pt_potential_score - st_current_score), 0, 0
    else:
        pt_lab = pt_labs[0]
        pt_current_score = potential_ta.get_score(selected_lab, template_schedule.id)
        st_potential_score = selected_ta.get_score(pt_lab, template_schedule.id)

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


def parse_semester_lab_dict(lab_dict, total_class_number):
    """
    Given POST data of a new semester, parse through it and define a list.

    This function operates under the assumption that there are exists
    properly formatted data within the dictionary.

    A single row of the POST data is as follows by index:
    0:  class name
    1:  subject
    2:  catalog ID
    3:  course ID
    4:  section
    5:  days
    6:  facility ID
    7:  facility building
    8:  instructor
    9:  start time
    10: end time
    """
    # create empty lab list
    lab_list = []
    lab_index = 0

    # loop through each given lab in the dictionary
    while lab_index < int(total_class_number):
        new_lab = []
        # pull relevant data
        new_lab.append(lab_dict['class_names'][lab_index])
        new_lab.append(lab_dict['subjects'][lab_index])
        new_lab.append(lab_dict['catalog_ids'][lab_index])
        new_lab.append(lab_dict['course_ids'][lab_index])
        new_lab.append(lab_dict['sections'][lab_index])
        new_lab.append(lab_dict['days'][lab_index])
        new_lab.append(lab_dict['facility_ids'][lab_index])
        new_lab.append(lab_dict['facility_buildings'][lab_index])
        new_lab.append(lab_dict['instructors'][lab_index])
        new_lab.append(lab_dict['start_times'][lab_index])
        new_lab.append(lab_dict['end_times'][lab_index])
        lab_list.append(new_lab)
        lab_index += 1
    return lab_list


def validate_course_id(course_id):
    """Ensure a given course ID does not already exist within the database."""
    try:
        Lab.objects.get(course_id=course_id)
        # course already exists in the database, cannot add it
        return (None, False)
    except Lab.DoesNotExist:
        # course does not exist, we can add it
        return (course_id, True)


def validate_days(days):
    """Ensure a given set of days is properly formatted for the database."""
    valid_days = ['M', 'T', 'W', 'Th', 'F']
    split_days = days.split(' ')
    for day in split_days:
        if day not in valid_days:
            return (None, False)
    return (days, True)


def validate_time(time):
    """Ensure a given time is properly formatted for the database."""
    try:
        time = datetime.strptime(time, '%H:%M').time()
        return (str(time), True)
    except ValueError:
        return (None, False)


def add_labs(labs_list, semester):
    """Add labs to the database for prevalidated data to a given semester."""
    try:
        for lab in labs_list:
            Lab.objects.create(
                class_name=lab[0],
                subject=lab[1],
                catalog_id=lab[2],
                course_id=lab[3],
                section=lab[4],
                days=lab[5],
                facility_id=lab[6],
                facility_building=lab[7],
                instructor=lab[8],
                start_time=lab[9],
                end_time=lab[10],
                semester=semester
            )
        # added all labs, return success
        return True
    except error as error:
        return False


def generate_semester_dictionary(semester_csv, time, year):
    """
    Handle a given semester CSV file and create a new semester object.

    Return True on success, False on failure.
    """
    try:
        semester_data = []
        csv_file = semester_csv.read().decode('UTF-8')
        csv_reader = csv.reader(StringIO(csv_file),
                                delimiter=',',
                                skipinitialspace=True)
        for row in csv_reader:
            lab_data = {}
            print(row)
            if len(row) == 11:
                lab_data['class_name'] = row[0].strip()
                lab_data['subject'] = row[1].strip()
                lab_data['catalog_id'] = row[2].strip()
                lab_data['course_id'] = validate_course_id(row[3].strip())
                lab_data['section'] = row[4].strip()
                lab_data['days'] = validate_days(row[5].strip())
                lab_data['facility_id'] = row[6].strip()
                lab_data['facility_building'] = row[7].strip()
                lab_data['instructor'] = row[8].strip()
                lab_data['start_time'] = validate_time(row[9].strip())
                lab_data['end_time'] = validate_time(row[10].strip())
                semester_data.append(lab_data)
        return semester_data
    except csv.Error as error:
        print(f'Error in line {csv_reader.line_num}: {error}')


def get_semester_cluster(current_semester):
    """Find two previous semesters and two future semesters."""
    curr_sem_string = current_semester['time'] + str(current_semester['year'])
    sorted_semesters = sort_semesters()
    index = 0
    bottom_ind = 0
    top_ind = 0
    for sem in sorted_semesters:
        if sem == curr_sem_string:
            if index > 2:
                bottom_ind = index - 2
            top_ind = index + 2
        index += 1
    return sorted_semesters[bottom_ind:top_ind+1]


# returns a string of the semester names in order (not objects)
def sort_semesters():
    """
    Return semester names in order.

    Note: Does not return objects, returns a list of strings.
    """
    time_encode_keys = {
        'SPR': 1,
        'SUM': 2,
        'FAL': 3,
        'WNT': 4
    }

    time_decode_keys = {
        1: 'SPR',
        2: 'SUM',
        3: 'FAL',
        4: 'WNT'
    }
    semesters = Semester.objects.all()
    semesters_tups = []
    sorted_semesters = []
    for semester in semesters:
        time = (time_encode_keys[semester.semester_time])
        year = (str(semester.year))
        semesters_tups.append(tuple((year, time)))

    semesters_tups.sort()
    for tup in semesters_tups:
        sem = time_decode_keys[tup[1]] + tup[0]
        sorted_semesters.append(sem)

    return sorted_semesters

def filter_out_unscored(ta_list):
    tas = []
    for ta in ta_list:
        if len(ta.scores.all()) != 0:
            tas.append(ta)

    return tas
