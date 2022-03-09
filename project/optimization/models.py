"""Models for optimized schedules."""
from django.db import models
from laborganizer.models import Lab, Semester
from teachingassistant.models import TA
from optimization.optimization_primary import (initialization)

class TemplateAssignment(models.Model):
    """Non-propogated TA assignments for use in the template schedule."""

    def __str__(self):
        """Define human readable object name."""
        return f'{self.lab}, {self.ta}'
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE,
                            blank=True, null=True)
    ta = models.ForeignKey(TA, on_delete=models.CASCADE,
                           blank=True, null=True)
    schedule_key = models.CharField('Schedule Key', max_length=10,
                                    blank=True, null=True)


class TemplateSchedule(models.Model):
    """A templated schedule for the LO to create before propogation."""

    def __str__(self):
        """Define human readable object name."""
        return f'{self.semester}, v{self.version_number}'

    def get_ta_by_name(self, ta_first_name, ta_last_name):
        """Get a TA by their name."""
        ta_list = TA.objects.all()

        for current_ta in ta_list:
            if current_ta.first_name == ta_first_name:
                if current_ta.last_name == ta_last_name:
                    return current_ta
        return None

    def lab_has_an_assignment(self, lab):
        """Check if a lab has an assignemnt in this schedule."""
        assignments = self.assignments.all()
        try:
            assignments.get(lab=lab)
            return True
        except:
            return False

    def get_lab_assignment(self, lab):
        """Get the assignment of a lab."""
        assignments = self.assignments.all()

        if self.lab_has_an_assignment(lab):
            lab_assignment = assignments.get(lab=lab)
            return lab_assignment

    def ta_assigned_to_lab(self, ta):
        """Check if a TA has an assignment in this schedule."""
        assignments = self.assignments.all()
        for assignment in assignments:
            temp = str(assignment).split(", ")
            temp = temp[1].split(" ")
            ta_of_interest = self.get_ta_by_name(temp[1], temp[2])
            if ta_of_interest == ta:
                return True
        return False

    def all_labs_have_assignment(self, labs):
        """Check if all labs in a given semester have assignments."""
        for lab in labs:
            if not self.lab_has_an_assignment(lab):
                return False
        return True

    def get_ta_lab_assignment(self, ta):
        """Get the assignment of a TA."""
        assignments = self.assignments.all()
        for assignment in assignments:
            temp = str(assignment).split(", ")
            temp = temp[1].split(" ")
            ta_of_interest = self.get_ta_by_name(temp[1], temp[2])
            if ta_of_interest == ta:
                return assignment
        return None

    def get_lab_object_from_assignment(self, assignment):
        """Get the lab object of an assignment."""
        lab_object = assignment.lab
        return lab_object

    def all_tas_assigned_to_lab(self, ta_list):
        """Check if all TA's have an assignment in this schedule."""
        for ta in ta_list:
            if not self.ta_assigned_to_lab(ta):
                return False
        return True

    def get_ta_score_for_lab(self, ta, lab):
        """Get the score of a TA for a lab in this schedule."""
        all_scores = ta.scores.all()
        lab_assignment = self.get_lab_assignment(lab)
        score_for_lab = all_scores.get(score_catalog_id=lab.catalog_id, semester=lab.semester, schedule_key = lab_assignment.schedule_key)
        return score_for_lab

    def remove_tas_from_list(self, ta_list, tas_being_removed):
        """Remove a TA from a Python list."""
        new_ta_list = []
        for ta in ta_list:
            for compar_ta in tas_being_removed:
                if ta != compar_ta:
                    new_ta_list.append(ta)
        return new_ta_list

    def initialize(self, tas, labs, priority_bonus=0):
        """Initialize this template schedule."""
        # give scores to all given TA's for this template
        initialization(tas, labs, self.id, priority_bonus)

        contracted_tas = []
        uncontracted_tas = []
        for ta in tas:
            if ta.contracted:
                contracted_tas.append(ta)
            else:
                uncontracted_tas.append(ta)

        # loop until all labs have a ta assigned
        while not self.all_labs_have_assignment(labs):
            # loop through all the Labs
            for lab in labs:
                # find a list of the highest scoring tas for a lab (if there
                # are multiple tas with the highest score)
                highest_scoring_tas = self.get_highest_scoring_tas(
                    contracted_tas, lab)
                # loop until lab is assigned
                while not self.lab_has_an_assignment(lab):
                    if self.all_tas_assigned_to_lab(contracted_tas):
                        if self.all_tas_assigned_to_lab(uncontracted_tas):
                            if self.lab_has_an_assignment(lab) is False:
                                self.assign(highest_scoring_tas[0], lab)
                        else:
                            highest_scoring_tas = self.get_highest_scoring_tas(
                                uncontracted_tas, lab)

                    # loop through the highest scoring TAs until a TA
                    # is assigned
                    for ta in highest_scoring_tas:
                        if not self.lab_has_an_assignment(lab):
                            # if the Ta is not already assigned to a lab
                            if not self.ta_assigned_to_lab(ta):
                                # Assign them to the current lab
                                self.assign(ta, lab)

                    # loop through highest scoring TAs
                    if self.lab_has_an_assignment(lab) is False:
                        for ta in highest_scoring_tas:
                            # if TA already assigned to a lab that is different
                            # than the current lab
                            if self.ta_assigned_to_lab(ta):
                                other_lab_assignment = self.get_ta_lab_assignment(highest_scoring_tas[0])
                                other_lab = self.get_lab_object_from_assignment(other_lab_assignment)
                                self.assign(ta, lab)

                                # Get scores for both labs
                                all_scores = highest_scoring_tas[0].scores.all()
                                other_lab_score = self.get_ta_score_for_lab(ta, other_lab)
                                current_lab = lab
                                current_lab_score = self.get_ta_score_for_lab(ta, current_lab)
                                # compare the two labs scores

                                # if ta score for current lab is greater
                                # then lab they are being placed
                                if current_lab_score.score > other_lab_score.score:
                                    # Unassign Ta from old lab
                                    self.unassign(other_lab)

                                    # Assign the TA to the current lab
                                    self.assign(ta, lab)

                                if current_lab_score.score <= other_lab_score.score:

                                    self.unassign(current_lab)
                                # otherwise the ta score for the old lab is
                                # greater then  or equal to the current lab and
                                # we move on to the next ta

                    # If the end of loop is reached and the lab still doesn't
                    # have an assignment generate a new highest scoring ta list
                    # with all old highest scores removed
                    new_ta_list = self.remove_tas_from_list(tas, highest_scoring_tas)
                    highest_scoring_tas = self.get_highest_scoring_tas(new_ta_list, lab)

        # loop through all given labs
        for lab in labs:
            # find the TA with the highest score given to this lab
            highest_scoring_tas = self.get_highest_scoring_tas(tas, lab)
            if len(highest_scoring_tas) > 0:
                # if there are multiple TA's with the same score for a lab,
                # assign the first TA
                self.assign(highest_scoring_tas[0], lab)
                # #assigning best scoring tas regardless of if they are already
                # assigned or not
                if not self.lab_has_an_assignment(lab):
                    self.assign(highest_scoring_tas[0], lab)

    def get_highest_scoring_tas(self, tas, lab):
        """
        Get the highest scoring TA/TA's for a given lab for this schedule.

        Return a list of all TA's with the highest score for the lab.
        NOTE: returning list in the event that multiple TA's have the
              same score
        """
        # determine the highest score
        max_score = 0
        ta_list = []
        for ta in tas:
            for score in ta.scores.filter(score_catalog_id=lab.catalog_id,
                                          schedule_key=self.id):
                if score.score > max_score:
                    max_score = score.score
        # get all the TA's with that score
        for ta in tas:
            for score in ta.scores.filter(score_catalog_id=lab.catalog_id,
                                          schedule_key=self.id):
                if score.score == max_score:
                    ta_list.append(ta)
        return ta_list

    def assign(self, ta, lab):
        """Create a new assignment for a TA in the template schedule."""
        # if there is a TA already assigned to the desired lab,
        # unassign them first
        self.unassign(lab)
        # create a new assignment object
        new_assignment = TemplateAssignment.objects.create(lab=lab,
                                                           ta=ta,
                                                           schedule_key=self.pk)
        new_assignment.save()
        # add the new object to the existing field
        self.assignments.add(new_assignment)
        # save changes
        self.save()

    def unassign(self, lab):
        """Remove the assigned TA from the selected lab."""
        for assignment in self.assignments.all():
            if assignment.lab == lab:
                assignment.delete()
                self.assignments.remove(assignment)
                self.save()
                return True
        return False

    def swap_assignments(self, from_assignment, to_assignment):
        """Swap two TA's assignments in this template."""
        temp_ta = to_assignment.ta
        to_assignment.ta = from_assignment.ta
        from_assignment.ta = temp_ta
        to_assignment.save()
        from_assignment.save()

    def get_assignment_from_id(self, course_id):
        """Get an assignment based on a given course ID."""
        for assignment in self.assignments.all():
            if assignment.lab.course_id == course_id:
                return assignment

    version_number = models.IntegerField('Schedule Version', default=0)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE,
                                 blank=True, null=True)
    assignments = models.ManyToManyField(TemplateAssignment, blank=True)
