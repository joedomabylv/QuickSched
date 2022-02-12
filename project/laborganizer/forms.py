"""Forms for the laborganizer app."""
from django import forms
from datetime import date


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
