"""Configuration information for laborganizer app."""
from django.apps import AppConfig


class LaborganizerConfig(AppConfig):
    """Metadata for laborganizer configuration."""

    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Lab Organizer'
    name = 'laborganizer'
