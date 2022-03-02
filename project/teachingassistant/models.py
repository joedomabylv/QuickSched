"""Models relating to Teaching Assistants."""
from django.db import models
from datetime import datetime


class ScorePair(models.Model):
    """A score pair representing a course catalog ID and a TA's score."""

    def __str__(self):
        """Define human readable object name."""
        return f'{self.score_catalog_id}:{self.score}'

    score_catalog_id = models.CharField('Catalog ID for score', max_length=10)
    score = models.IntegerField('Score')


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

    def get_all_assigned_semesters(self):
        """
        Get a list of all semesters this TA is assigned to.

        Return a Python list of tuples with index 0 begin the time and
        index 1 being the year, i.e. ('SPR', 2022).
        """
        semester_list = []
        for semester in self.assigned_semesters.all():
            semester_list.append((semester.semester_time, semester.year))
        return semester_list

    def get_all_assigned_labs(self):
        """
        Get a list of all labs this TA is assigned to.

        Returns the name of the lab in human readable format.
        """
        lab_list = []
        for lab in self.assigned_labs.all():
            lab_list.append(lab.__str__())
        return ', '.join(lab_list)

    # define choice variable
    YEAR = (
        ('FR', 'Freshman'),
        ('SO', 'Sophomore'),
        ('JR', 'Junior'),
        ('SR', 'Senior'),
        ('GR', 'Graduate')
        )

    # define fields
    first_name = models.CharField('TA\'s first name',
                                  max_length=50, default='missing')
    last_name = models.CharField('TA\'s last name',
                                 max_length=50, default='missing')
    student_id = models.CharField('TA\'s student ID', max_length=50,
                                  unique=True, blank=True)

    contracted = models.BooleanField('Contracted', blank=True, null=True)

    # experience needs to be configured to account for whatever
    # we want to display experience/relevant skills as
    experience = models.CharField('TA\'s experience', max_length=100,
                                  blank=True)

    year = models.CharField('TA\'s current year', max_length=2,
                            choices=YEAR, blank=True)

    holds_key = models.IntegerField('Primary Holds key', blank=True,
                                    null=True, unique=True)

    availability_key = models.IntegerField('Primary Availability key',
                                           blank=True, null=True, unique=True)

    scores = models.ManyToManyField(ScorePair, blank=True)

    assigned_semesters = models.ManyToManyField("laborganizer.Semester",
                                                blank=True)

    assigned_labs = models.ManyToManyField("laborganizer.Lab",
                                           blank=True)


class ClassTime(models.Model):
    """
    Represent a pair of times for a single TA.

    1. Start time = the time their class starts
    2. End time = the time their class ends
    3. Days = the days these times are for
    """

    class Meta:
        """Meta information for a ClassTime object."""

        verbose_name = 'Class Time'
        verbose_name_plural = 'Class Times'

    def __str__(self):
        """Human readable object name."""
        return f'{self.start_time}-{self.end_time}'

    def join_days(days_list):
        """Given a Python list of days, join them by commas."""
        return ','.join(days_list)

    def get_days(self):
        """Return a Python list of the days attached to this time."""
        return self.days.split(',')

    # key to TA
    ta = models.ForeignKey(TA, on_delete=models.CASCADE)

    # times
    start_time = models.TimeField(auto_now=False, auto_now_add=False)
    end_time = models.TimeField(auto_now=False, auto_now_add=False)

    # days for these times
    days = models.CharField('Days', max_length=10, blank=True, null=True)


class Availability(models.Model):
    """Object representing a single TA's availability."""

    class Meta:
        """Metadata regarding Availability objects."""

        verbose_name = 'Availability'
        verbose_name_plural = 'Availability\'s'

    def __str__(self):
        """Human readable object name."""
        return f'{self.ta}\'s Availability'

    def delete_times(self):
        """Delete all the class times for a TA."""
        print(len(self.class_times.all()))

        # remove the times from the availability object
        for time in self.class_times.all():
            self.class_times.remove(time)

        # delete actual ClassTime objects
        ClassTime.objects.filter(ta=self.ta).delete()

    def edit_time(self, time_list):
        """Create a new ClassTime object for this TA."""
        # delete the existing class times, if any
        self.delete_times()

        # create new class times for each object
        for new_time in time_list:
            # splice the days from the current index
            days = new_time[2:]

            # join the days list
            days = ClassTime.join_days(days)

            # create a new class time object and assign it to this field
            self.class_times.create(start_time=new_time[0],
                                    end_time=new_time[1],
                                    days=days,
                                    ta=self.ta)

    def get_class_times(self):
        """Return a dictionary of the TA's class times."""
        time_list = []
        for time in self.class_times.all():
            time_list.append(time.__str__())
        return time_list

    class_times = models.ManyToManyField(ClassTime)

    # key to TA
    ta = models.OneToOneField(TA, on_delete=models.CASCADE)


class Holds(models.Model):
    """Possible holds to be applied to TA accounts."""

    class Meta:
        """Metadata regarding Holds objects."""

        verbose_name = 'Holds'
        verbose_name_plural = 'Holds'

    def __str__(self):
        """Human readable object name."""
        return f'{self.ta}\'s Holds'

    # if the TA has not completed the initialization of their profile
    # NOTE: defaults to true such that a new TA will be required
    #       to update their profile before being scheduled
    incomplete_profile = models.BooleanField('Incomplete profile',
                                             default=True)

    # if the TA needs to update their availability
    update_availability = models.BooleanField('Update availability',
                                              default=False)

    # if the TA needs to update their experience
    update_experience = models.BooleanField('Update experience',
                                            default=False)

    # key to TA
    ta = models.OneToOneField(TA, on_delete=models.CASCADE, verbose_name='TA')
