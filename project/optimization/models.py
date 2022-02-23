"""Models for optimized schedules."""
from django.db import models
from laborganizer.models import Lab, Semester
from teachingassistant.models import TA


class TemplateAssignments(models.Model):
    """Non-propogated TA assignments for use in the template schedule."""

    def __str__(self):
        """Define human readable object name."""
        return f'{self.lab}, {self.ta}'

    lab = models.ManyToManyField(Lab)
    ta = models.ManyToManyField(TA)


class TemplateSchedule(models.Model):
    """A templated schedule for the LO to create before propogation."""

    def __str__(self):
        """Define human readable object name."""
        return f'Schedule: {self.semester}, v{self.version_number}'

    version_number = models.CharField('Schedule Version', max_length=50)
    semester = models.ManyToManyField(Semester)
    assignments = models.ManyToManyField(TemplateAssignments)
