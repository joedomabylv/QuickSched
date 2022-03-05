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

    def initialize(self, tas, labs):
        """Initialize this template schedule."""
        # give scores to all given TA's for this template
        initialization(tas, labs, self.id)
        # loop through all given labs
        for lab in labs:
            # find the TA with the highest score given to this lab
            highest_scoring_tas = self.get_highest_scoring_tas(tas, lab)
            if len(highest_scoring_tas) > 0:
                # if there are multiple TA's with the same score for a lab,
                # assign the first TA
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
