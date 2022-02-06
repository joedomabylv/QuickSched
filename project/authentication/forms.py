"""Custom forms for the authentication app."""
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from .models import CustomUserModel


class CustomPasswordChangeForm(PasswordChangeForm):
    """Customize the password change form provided by Django for QuickSched."""

    old_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control',
               'type': 'password'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control',
               'type': 'password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control',
               'type': 'password'}))

    class Meta:
        """Define metadata for custom password change form."""

        model = CustomUserModel
        fields = ('old_password', 'new_password1', 'new_password2')
