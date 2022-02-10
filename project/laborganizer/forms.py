"""Forms for the laborganizer app."""
from django import forms
from datetime import date
from .models import Semester


class SelectSemesterForm(forms.Form):
    """Form used by LO to select a semester to display."""

    field_attributes = {'class': 'my-2 form-select', 'style': 'width:20%'}

    def generate_semester_tuples():
        """Generate a list of tuples to be presented as choices within the form."""
        semesters = Semester.objects.all()
        semester_list = []
        for semester in semesters:
            # key and value are the same for database representation
            current_tuple = (semester.semester_time + '' + semester.year,
                             semester.semester_time + '' + semester.year)
            semester_list.append(current_tuple)
        return semester_list

    SEMESTERS = generate_semester_tuples()

    semester_selection = forms.ChoiceField(label='Semester Selection', choices=SEMESTERS,
                                           widget=forms.Select(attrs=field_attributes))


class NewSemesterForm(forms.Form):
    """Form used by a LO to input a new semester."""

    field_attributes = {'class': 'my-2 form-select', 'style': 'width:50%'}

    TIMES = (
        ('SPR', 'Spring'),
        ('SUM', 'Summer'),
        ('FAL', 'Fall'),
        ('WNT', 'Winter')
    )

    def get_10_years():
        """
        Generate a list of tuples of 10 years.

        Beginning with the current year, assign keys and values.
        Note that keys/values are the same, allowing the list to
        remain dynamic.
        """
        year = date.today().year
        years = [(year, year)]
        for index in range(10):
            year += 1
            years.append((year, year))
        return years

    # define the dynamic year list
    YEARS = get_10_years()

    year = forms.ChoiceField(label='Year', choices=YEARS,
                             widget=forms.Select(attrs=field_attributes))
    semester_time = forms.ChoiceField(label='Semester Time', choices=TIMES,
                                      widget=forms.Select(attrs=field_attributes))
