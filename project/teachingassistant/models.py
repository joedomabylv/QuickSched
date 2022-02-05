"""Models relating to Teaching Assistants."""
from django.db import models
from laborganizer.models import Lab
from authentication.models import CustomUserModel


class Availability(models.Model):
    """Object representing a single TA's availability."""

    monday_start = models.TimeField(auto_now=False, auto_now_add=False)
    monday_end = models.TimeField(auto_now=False, auto_now_add=False)
    tuesday_start = models.TimeField(auto_now=False, auto_now_add=False)
    tuesday_end = models.TimeField(auto_now=False, auto_now_add=False)
    wednesday_start = models.TimeField(auto_now=False, auto_now_add=False)
    wednesday_end = models.TimeField(auto_now=False, auto_now_add=False)
    thursday_start = models.TimeField(auto_now=False, auto_now_add=False)
    thursday_end = models.TimeField(auto_now=False, auto_now_add=False)
    friday_start = models.TimeField(auto_now=False, auto_now_add=False)
    friday_end = models.TimeField(auto_now=False, auto_now_add=False)
    saturday_start = models.TimeField(auto_now=False, auto_now_add=False)
    saturday_end = models.TimeField(auto_now=False, auto_now_add=False)
    sunday_start = models.TimeField(auto_now=False, auto_now_add=False)
    sunday_end = models.TimeField(auto_now=False, auto_now_add=False)


class TA(models.Model):
    """TA Object. Primary key is predefined as an integer value by Django."""

    class Meta:
        """Metadata regarding TA's."""

        verbose_name = 'TA'
        verbose_name_plural = 'TA\'s'

    def __str__(self):
        """Human readable class name, for admin site."""
        human_readable_name = ""
        if self.year == 'GR':
            # flag the TA as a 'G'TA
            # NOTE: we can change the admin site to display an arrow or
            #       something if the TA is a GTA (or if they're contracted)
            human_readable_name += 'G'
        human_readable_name += 'TA ' + self.first_name + ' ' + self.last_name
        return human_readable_name

    # define choice variable
    YEAR = (
        ('FR', 'Freshman'),
        ('SO', 'Sophomore'),
        ('JR', 'Junior'),
        ('SR', 'Senior'),
        ('GR', 'Graduate')
        )

    # define fields
    first_name = models.CharField('TA\'s first name', max_length=50)
    last_name = models.CharField('TA\'s last name', max_length=50)
    student_id = models.CharField('TA\'s student ID', max_length=50,
                                  unique=True)
    email = models.EmailField('TA\'s email', max_length=250)

    user_model = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, blank=True, null=True)

    # availability still needs to be configured to account for different days
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE, blank=True, null=True)

    contracted = models.BooleanField('Contracted', blank=True)

    # experience needs to be configured to account for whatever
    # we want to display experience/relevant skills as
    experience = models.CharField('TA\'s experience', max_length=100,
                                  blank=True)
    year = models.CharField('TA\'s current year', max_length=2,
                            choices=YEAR, blank=True)
    assignments = models.ManyToManyField(Lab, blank=True)
