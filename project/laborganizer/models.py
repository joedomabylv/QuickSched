"""Models relating to Lab Organizers."""
from django.db import models


class Semester(models.Model):
    """
    Semester Object. Primary key is predefined as an integer by Django.

    One Semester contains many labs.
    TODO: Implement a check that warns the LO if a semester already exists
          with a given time/year, i.e. 'you already have a SPR2022 semester,
          did you want another one?'
    """

    class Meta:
        """Metadata regarding a Semester."""

        verbose_name = 'Semester'
        verbose_name_plural = 'Semesters'

    def __str__(self):
        """Human readable class name, for admin site."""
        return self.semester_time + self.year

    TIMES = (
        ('SPR', 'Spring'),
        ('SUM', 'Summer'),
        ('FAL', 'Fall'),
        ('WNT', 'Winter')
    )

    # Year is subject to change from CharField to something more intelligent.
    # Perhaps a list of choices ranging from current year to 10 years from now?
    year = models.CharField('Calendar year', max_length=5)
    semester_time = models.CharField('Time held', max_length=3, choices=TIMES)
    # labs = link labs? maybe just a counter


class Lab(models.Model):
    """Lab Object related to a single semester."""

    class Meta:
        """Metadata regarding a Lab Object."""

        verbose_name = 'Lab'
        verbose_name_plural = 'Labs'

    def __str__(self):
        """Human readable class name, for admin site."""
        return self.class_name + ', ' + self.catalog_id

    class_name = models.CharField("Class name", default="N/A", max_length=50)
    course_id = models.CharField("Course ID", max_length=10, blank=True)
    catalog_id = models.CharField("Catalog ID", max_length=10, blank=True)
    section = models.CharField("Section", max_length=10, blank=True)

    # change to list or something?
    day = models.CharField("Day", max_length=10)

    facility_id = models.CharField("Facility ID", max_length=20, blank=True)
    facility_building = models.CharField("Facility Building", max_length=50,
                                         blank=True)
    instructor = models.CharField("Instructor", max_length=50, blank=True)

    # change to list or something?
    time = models.CharField("Time", max_length=50)

    staffed = models.BooleanField(default=False)

    semester = models.ForeignKey(
        'Semester',
        on_delete=models.CASCADE,
        verbose_name='Semester',
        null=True
    )
