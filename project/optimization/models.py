"""Models for optimized schedules."""
from django.db import models
from laborganizer.models import Lab, Semester
from teachingassistant.models import TA


class TemplateAssignment(models.Model):
    """Non-propogated TA assignments for use in the template schedule."""

    def __str__(self):
        """Define human readable object name."""
        return f'{self.lab}, {self.ta}'

    lab = models.ManyToManyField(Lab)
    ta = models.ManyToManyField(TA)
    semester = models.ManyToManyField(Semester)


class TemplateSchedule(models.Model):
    """A templated schedule for the LO to create before propogation."""

    def __str__(self):
        """Define human readable object name."""
        return f'Schedule: {self.semester}, v{self.version_number}'

    def assign(self, ta, lab):
        """Create a new assignment for a TA in the template schedule."""
        # create a new assignment object
        new_assignment = TemplateAssignment.create(lab=lab, ta=ta,
                                                   semester=self.semester)
        # add the new object to the existing field
        self.assignments.add(new_assignment)
        # save changes
        self.save()

    def unassign(self, ta, lab):
        """Remove an assignment for a TA within the template schedule."""
        # remove the TA from the assignments field
        self.assignments.remove(ta=ta, lab=lab, semester=self.semester)
        # save changes to overall schedule
        self.save()

        # delete the TemplateAssignment object associated with that TA
        assignment = TemplateAssignment.objects.get(ta=ta, lab=lab,
                                                    semester=self.semester)
        assignment.delete()
        # save changes to assignment object
        assignment.save()

    version_number = models.CharField('Schedule Version', max_length=50)
    semester = models.ManyToManyField(Semester)
    assignments = models.ManyToManyField(TemplateAssignment)
