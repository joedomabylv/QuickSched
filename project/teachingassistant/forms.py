"""Forms for the teachingassistant app."""
from django import forms


class NewTAForm(forms.Form):
    """Form to represent a new TA."""

    YEAR = (
        ('FR', 'Freshman'),
        ('SO', 'Sophomore'),
        ('JR', 'Junior'),
        ('SR', 'Senior'),
        ('GR', 'Graduate')
        )

    field_attributes = {'class': 'my-2 form-control', 'style': 'width:50%'}

    first_name = forms.CharField(label='First name', max_length=50,
                                 widget=forms.TextInput(attrs=field_attributes))
    last_name = forms.CharField(label='Last name', max_length=50,
                                widget=forms.TextInput(attrs=field_attributes))
    student_id = forms.CharField(label='Student ID', max_length=50,
                                 widget=forms.TextInput(attrs=field_attributes))

    # availability still needs to be configured to account for different days
    # availability = models.ForeignKey(Availability, on_delete=models.CASCADE, blank=True, null=True)

    # experience needs to be configured to account for whatever
    # we want to display experience/relevant skills as
    experience = forms.CharField(label='Experience', max_length=100,
                                 widget=forms.TextInput(attrs=field_attributes))

    year = forms.ChoiceField(label='Current year', choices=YEAR,
                             widget=forms.Select(attrs=field_attributes))


class NewTAAvailabilityForm(forms.Form):
    """Form to represent a new TA's availability."""

    time_attributes = {
        'class': 'mb-4 form-control',
        'type': 'time',
        'style': 'width:25%',
        }

    monday_start = forms.TimeField(widget=forms.TimeInput(attrs=time_attributes))
    monday_end = forms.TimeField(widget=forms.TimeInput(attrs=time_attributes))
    tuesday_start = forms.TimeField(widget=forms.TimeInput(attrs=time_attributes))
    tuesday_end = forms.TimeField(widget=forms.TimeInput(attrs=time_attributes))
    wednesday_start = forms.TimeField(widget=forms.TimeInput(attrs=time_attributes))
    wednesday_end = forms.TimeField(widget=forms.TimeInput(attrs=time_attributes))
    thursday_start = forms.TimeField(widget=forms.TimeInput(attrs=time_attributes))
    thursday_end = forms.TimeField(widget=forms.TimeInput(attrs=time_attributes))
    friday_start = forms.TimeField(widget=forms.TimeInput(attrs=time_attributes))
    friday_end = forms.TimeField(widget=forms.TimeInput(attrs=time_attributes))
    saturday_start = forms.TimeField(widget=forms.TimeInput(attrs=time_attributes))
    saturday_end = forms.TimeField(widget=forms.TimeInput(attrs=time_attributes))
    sunday_start = forms.TimeField(widget=forms.TimeInput(attrs=time_attributes))
    sunday_end = forms.TimeField(widget=forms.TimeInput(attrs=time_attributes))
