"""Admin information for user authentication."""
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from authentication.models import CustomUserModel
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError


class CustomUserCreationForm(forms.ModelForm):
    """Form for creating new users."""

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password Confirmation',
                                widget=forms.PasswordInput)

    class Meta:
        """Metadata regarding new user form."""

        model = CustomUserModel
        fields = ('email', 'first_name', 'last_name')

    def clean_password(self):
        """Check if the two passwords match."""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match!')
        return password2

    def save(self, commit=True):
        """Save the users password in a hash."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    """Form for updating the custom user model."""

    password = ReadOnlyPasswordHashField()

    class Meta:
        """Metadata regarding the user change form."""

        model = CustomUserModel
        fields = ('email', 'password', 'first_name', 'last_name')


class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for the user.

    Extends UserAdmin.
    """

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('email', 'first_name', 'last_name', 'date_joined')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}))
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
            }),
        )

    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    ordering = ('email',)
    exclude = ('id', 'is_admin', 'is_staff', 'is_active', 'is_superuser')

    filter_horizontal = ()


admin.site.register(CustomUserModel, CustomUserAdmin)
admin.site.unregister(Group)
