from django.db import models


class EmailInformation(models.Model):
    """Email information used in account creation."""

    def __str__(self):
        """Define human readable object name."""
        return 'Email Information'

    def set_new_accounts(self, new_accounts_list):
        """
        Set the objects 'new_accounts' field.

        Convert from a Python list to a string.
        """
        self.new_accounts = ''.join(new_accounts_list)
        self.save()

    def get_new_accounts(self):
        """
        Return a Python list of new accounts.

        Convert from a string to a Python list.
        """
        return self.new_accounts.split(' ')

    def set_returning_accounts(self, returning_accounts_list):
        """
        Set the objects 'returning_accounts' field.

        Convert from Python list to a string.
        """
        self.returning_accounts = ''.join(returning_accounts_list)
        self.save()

    def get_returning_accounts(self):
        """
        Return a Python list of returning accounts.

        Convert from a string to a Python list.
        """
        return self.returning_accounts.split(' ')

    def clear_all_fields(self):
        """
        Clear all fields in the object.

        Used before entering new data.
        """
        self.new_accounts = ''
        self.returning_accounts = ''
        self.old_email_file_name = ''

    new_accounts = models.TextField(blank=True, null=True)
    returning_accounts = models.TextField(blank=True, null=True)
    old_email_file_name = models.CharField(max_length=100)
