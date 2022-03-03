"""Primary optimization function/functions."""


def calculate_score(ta, lab, template_id):
    """Calculate the score for a TA for a given lab."""
    total_score = 0

    # get the weight of an experience score, hardcoded for now
    EXP_WEIGHT = 10

    ta_experience = ta.get_experience()

    ta_availability = ta.get_availability()

    # check if the TA has experience in teaching the lab
    for experience in ta_experience:
        experience_subject = experience[0]
        experience_id = experience[1]
        if (experience_subject == lab.subject
            and experience_id == lab.catalog_id):
            total_score += EXP_WEIGHT

    # check if the TA has the availability to teach the lab
    for time in ta_availability.values():
        if not available(lab, time):
            total_score -= 999

    # assign the score to a TA object
    ta.assign_score(total_score, lab, template_id)


def initialization(tas, labs, template_id):
    """
    Primary initialization function for all TA scores.

    Given a list of TA's and labs, assign a score to each TA for each Lab.
    """
    # calculate all scores
    for lab in labs:
        for ta in tas:
            calculate_score(ta, lab, template_id)


def recalc_scores(ta, labs):
    """Calculate scores for all labs for a single TA."""
    for lab in labs:
        calculate_score(ta, lab)


def available(lab, ta_time):
    """
    Check if the time of a lab and the availability of a TA overlap.

    NOTE: The TA time is when the TA IS UNAVAILABLE
    """
    lab_days = lab.get_days()
    ta_days = ta_time['days']
    ta_start_time = ta_time['start_time']
    ta_end_time = ta_time['end_time']
    # if at least one of the lab days is within the ta days, check if the times
    # overlap
    if bool(set(lab_days) & set(ta_days)):
        # check for time overlap

        # TA class starts during the lab
        if ((ta_start_time >= lab.start_time and ta_start_time <= lab.end_time)
            # TA class ends during a lab
            or (ta_end_time >= lab.start_time and ta_end_time <= lab.end_time)
            # lab starts during TA class
            or (lab.start_time >= ta_start_time and lab.start_time <= ta_end_time)
            # lab ends during TA class
            or (lab.end_time >= ta_start_time and lab.end_time <= ta_end_time)):
            # times overlap, return false
            return False
    # times do not overlap or do not share a day, return true
    return True
