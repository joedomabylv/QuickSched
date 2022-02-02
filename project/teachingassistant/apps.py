"""Configuration information for teachingassistant app."""
from django.apps import AppConfig


class TeachingassistantConfig(AppConfig):
    """Metadata for teachingassistant configuration."""

    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Teaching Assistant'
    verbose_name_plural = 'Teaching Assistant\'s'
    name = 'teachingassistant'
