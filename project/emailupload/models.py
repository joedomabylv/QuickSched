from django.db import models


class NewAccountEmails(models.Model):
    """Email information used in account creation."""

    new_account = models.EmailField(blank=True, null=True)

class ReturningAccountEmails(models.Model):
    """Email information used in account creation."""

    returning_account = models.EmailField(blank=True, null=True)
