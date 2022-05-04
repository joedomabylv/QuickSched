"""Models for optimized schedules."""
from django.db import models
from laborganizer.models import Semester, Lab
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


    def lab_has_an_assignment(self, lab):
        assignments = self.assignments.all()
        for assignment in assignments:
            if assignment.lab == lab:
                return True
        return False
    def get_lab_assignment(self, lab):
        assignments = self.assignments.all()

        if self.lab_has_an_assignment(lab):
            lab_assignment = assignments.get(lab=lab)
            return lab_assignment

    """get other labs score"""
    """Function: Check if a given ta has a lab assigned to them"""
    def ta_assigned_to_lab(self, ta):
        assignments = self.assignments.all()
        for assignment in assignments:
            if assignment.ta == ta:
                return True
        return False

    def all_labs_have_assignment(self, labs):

        for lab in labs:
            if not self.lab_has_an_assignment(lab):
                return False
        return True

    def get_ta_lab_assignment(self, ta):
        assignments = self.assignments.all()
        ta_assignments = []
        for assignment in assignments:
            if assignment.ta == ta:
                ta_assignments.append(assignment)
        return ta_assignments
    def get_lab_object_from_assignment(self, assignment):
        lab_object = assignment.lab
        return lab_object

    """Function: Check if all tas taken in are assigned to a lab"""
    def all_tas_assigned_to_lab(self, ta_list):
        if ta_list == []:
            return True
        for ta in ta_list:
            if not self.ta_assigned_to_lab(ta):
                return False
        return True

    def get_ta_score_for_lab(self, ta, lab):
        all_scores = ta.scores.all()

        lab_assignment = self.get_lab_assignment(lab)
        score_for_lab = all_scores.get(score_catalog_id=lab.catalog_id, semester=lab.semester, schedule_key = lab_assignment.schedule_key)
        return score_for_lab

    def assign_all_tas_from_list(self, ta_list, lab_list):
            #loop through the labs
            contracted_tas = []
            uncontracted_tas = []
            for ta in ta_list:
                if ta.contracted:
                    contracted_tas.append(ta)
                else:
                    uncontracted_tas.append(ta)

            while (not self.all_tas_assigned_to_lab(contracted_tas)
                   and not self.all_labs_have_assignment(lab_list)):
                for lab in lab_list:
                    if not self.all_tas_assigned_to_lab(contracted_tas):
                        if not self.lab_has_an_assignment(lab):
                            while not self.lab_has_an_assignment(lab):
                                # get list of highest scoring tas for lab
                                highest_scoring_tas = self.get_highest_scoring_tas(contracted_tas, lab)
                                # if all of the highest scoring tas are already assigned
                                while self.all_tas_assigned_to_lab(highest_scoring_tas):
                                    # create new highest scoring ta list with old highest scoreres removed
                                    new_ta_list = self.remove_tas_from_list(contracted_tas , highest_scoring_tas)
                                    highest_scoring_tas = self.get_highest_scoring_tas(contracted_tas, lab)

                                #loop through highest scoring tas
                                if highest_scoring_tas != []:
                                    for ta in highest_scoring_tas:
                                        if not self.lab_has_an_assignment(lab):
                                            #if the ta is not already assigned
                                            if not self.ta_assigned_to_lab(ta):
                                                self.assign(ta, lab)

            if not self.all_labs_have_assignment(lab_list):
                while (not self.all_tas_assigned_to_lab(uncontracted_tas)
                       and not self.all_labs_have_assignment(lab_list)):
                    for lab in lab_list:
                        if not self.all_tas_assigned_to_lab(uncontracted_tas):
                            if not self.lab_has_an_assignment(lab):
                                while not self.lab_has_an_assignment(lab):
                                    # get list of highest scoring tas for lab
                                    highest_scoring_tas = self.get_highest_scoring_tas(uncontracted_tas, lab)

                                    # if all of the highest scoring tas are already assigned
                                    while self.all_tas_assigned_to_lab(highest_scoring_tas):
                                        # create new highest scoring ta list with old highest scoreres removed
                                        new_ta_list = self.remove_tas_from_list(uncontracted_tas , highest_scoring_tas)
                                        highest_scoring_tas = self.get_highest_scoring_tas(uncontracted_tas, lab)

                                    #loop through highest scoring tas
                                    if highest_scoring_tas != []:
                                        for ta in highest_scoring_tas:
                                            if not self.lab_has_an_assignment(lab):
                                                #if the ta is not already assigned
                                                if not self.ta_assigned_to_lab(ta):
                                                    self.assign(ta, lab)

            for lab in lab_list:
                highest_scoring_tas = self.get_highest_scoring_tas(contracted_tas, lab)
                num_assignments = 1
                for ta in highest_scoring_tas:
                    num_assignments = len(self.get_ta_lab_assignment(ta))
                    if num_assignments < 3:
                        if not self.lab_has_an_assignment(lab):
                            self.assign(ta, lab)

            for lab in lab_list:
                highest_scoring_tas = self.get_highest_scoring_tas(uncontracted_tas, lab)
                num_assignments = 1
                for ta in highest_scoring_tas:
                    num_assignments = len(self.get_ta_lab_assignment(ta))
                    if num_assignments < 3:
                        if not self.lab_has_an_assignment(lab):
                            self.assign(ta, lab)


    def remove_tas_from_list(self, ta_list, tas_being_removed):
        new_ta_list = []
        for ta in ta_list:
            for compar_ta in tas_being_removed:
                if ta != compar_ta:
                    new_ta_list.append(ta)
        return new_ta_list


    def initialize(self, tas, labs, priority_bonus = 0):
        """Initialize this template schedule."""
        # give scores to all given TA's for this template
        initialization(tas, labs, self.id, priority_bonus)

        self.assign_all_tas_from_list(tas, labs)


    def get_highest_scoring_tas(self, tas, lab):
        """
        Get the highest scoring TA/TA's for a given lab for this schedule.

        Return a list of all TA's with the highest score for the lab.
        NOTE: returning list in the event that multiple TA's have the
              same score
        """
        # determine the highest score
        max_score = -99999
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

    def has_one_assignment(self):
        """Check if this template has at least one TA assigned to a lab."""
        for assignment in self.assignments.all():
            if assignment.ta is not None:
                return True
        return False

    def get_semester(self):
        """Get the semester this schedule is for."""
        return self.semester

    version_number = models.IntegerField('Schedule Version', default=0)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE,
                                 blank=True, null=True)
    assignments = models.ManyToManyField(TemplateAssignment, blank=True)


class History(models.Model):
    """History stack for swapped TA's."""

    def undo_bilateral_switch(self, template_schedule, from_assignment, to_assignment):
        """Undo a switch."""
        template_schedule.swap_assignments(from_assignment, to_assignment)

    ta_1 = models.ManyToManyField("teachingassistant.TA",
                                  blank=True, related_name='ta_1')
    ta_2 = models.ManyToManyField("teachingassistant.TA",
                                  blank=True, related_name='ta_2')
    lab_1 = models.ManyToManyField(Lab, blank=True, related_name='lab_1')
    lab_2 = models.ManyToManyField(Lab, blank=True, related_name='lab_2')

    is_assignment = models.BooleanField(default=False)

    temp_sched = models.ForeignKey(TemplateSchedule, on_delete=models.CASCADE, related_name='his_nodes', null=True)
    relative_node_id = models.IntegerField(null=True)
