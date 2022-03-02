"""Models for optimized schedules."""
from django.db import models
from laborganizer.models import Lab, Semester
from teachingassistant.models import TA


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


    version_number = models.IntegerField('Schedule Version', default=0)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE,
                                 blank=True, null=True)
    assignments = models.ManyToManyField(TemplateAssignment, blank=True)
