"""View management for EmailUpload app. 'eu' prefix = email upload."""
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage, default_storage
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.mail import send_mail, send_mass_mail
from quicksched import settings
from django.contrib import messages
from django.forms import ValidationError
from django.utils.datastructures import MultiValueDictKeyError
from .models import NewAccountEmails, ReturningAccountEmails
from authentication.models import CustomUserModel
import csv
import os


def eu_upload(request):
    """Home route, only uploading emails."""
    if request.method == 'POST':

        # get the uploaded document
        # [NEED TO HAVE NGINX DO FILE HANDLING UPON DEPLOYMENT]
        try:
            uploaded_file = request.FILES['document']
        except MultiValueDictKeyError:
            messages.error(request, 'Please upload a csv file before proceeding!')
            return render(request, 'emailupload/ta_add.html')

        # open the file system
        fs = FileSystemStorage()

        # ensure the file attempting to be uploaded is a CSV file
        if not uploaded_file.name.endswith('.csv'):
            messages.error(request, 'This file is not a CSV!')
            return render(request, 'emailupload/ta_add.html')

        # save the uploaded file to the default 'media' directory, then
        # initialize lists and file reader
        new_emails = fs.save(uploaded_file.name, uploaded_file)
        new_emails_file = default_storage.open(os.path.join('', new_emails), 'r')
        returning_accounts = []
        new_accounts = []
        new_emails = []
        old_emails = []
        new_file_reader = csv.reader(new_emails_file, delimiter=',')

        # if there are any returning emails from a previous upload, make sure
        # they are not prompted to make a new account
        # open the file of previous emails

        # generate list of old emails
        for old_user in CustomUserModel.objects.all():
            old_emails.append(old_user.email)

        # generate list of new emails
        for new_user in new_file_reader:
            new_emails = new_emails + new_user

        # check for overlap between the two lists, populate list of
        # returning accounts
        for old_email in old_emails:
            if old_email in new_emails:
                returning_accounts.append(old_email)

        # check for new emails/users, populate list of new accounts
        for new_email in new_emails:
            if new_email not in returning_accounts:
                new_accounts.append(new_email)

        # Check for validity of new accounts
        for account in new_accounts:
            # try to validate
            try:
                validate_email(account.strip())
            except ValidationError as error:
                # TODO: get and display ALL invalid emails, not just one
                messages.error(request, account + ' is not a valid email for this roster!')
                print(error)
                return redirect('../ta_add')

        # set email information block
        set_email_info(new_accounts, returning_accounts)

        context = {"new_accounts": new_accounts,
                   "returning_accounts": returning_accounts}

        default_storage.delete(os.path.join('', uploaded_file.name))

        # direct the user to the confirmation page
        return render(request, 'emailupload/ta_roster_confirm.html', context)

    # everything else failed, return them to the upload view
    return render(request, 'emailupload/ta_add.html')


def set_email_info(new_accounts, returning_accounts):
    """Set/initialize the Email Information object."""
    NewAccountEmails.objects.all().delete()
    ReturningAccountEmails.objects.all().delete()

    for account in new_accounts:
        acct = NewAccountEmails(new_account=account.strip())
        acct.save()

    for account in returning_accounts:
        acct = ReturningAccountEmails(returning_account=account.strip())
        acct.save()

def cancel_roster(request):
    return redirect('../ta_add')


def confirm_emails(request):
    """Confirm the emails in all accounts, new or returning."""
    # get email information
    new_accounts = NewAccountEmails.objects.all().values_list('new_account', flat=True)
    returning_accounts = ReturningAccountEmails.objects.all().values_list('returning_account', flat=True)

    # generate passwords for new emails
    passwords = []
    for account in new_accounts:
        passwords.append(get_random_string(12))


    email_messages = []

    # welcome email
    index = 0
    if len(new_accounts) > 0:
        while index < len(new_accounts):
            to_email = new_accounts[index]
            temp_pass = passwords[index]
            welcome_subject = "Welcome to QuickSched!"
            welcome_message = """Hello! \n Welcome to Quicksched!\nYour Account has successfully been created.
            \n\n To finish your registration, please use your email and temporary password down below to login.
            You will be prompted to change it upon your login.\n\n Temporary Password: """ + temp_pass
            from_email = settings.EMAIL_HOST_USER
            email_messages.append((welcome_subject, welcome_message, from_email, [to_email]))
            index += 1
        send_mass_mail(tuple(email_messages), fail_silently=False)

    # returning email
    if len(returning_accounts) > 0:
        welcome_subject = "Welcome to back to QuickSched!"
        welcome_message = """Hello!\n This email is here to let you know that your email has been registered back in the system.
        Please sign in and update your schedule and other information about your availability and qualifications."""
        from_email = settings.EMAIL_HOST_USER
        send_mail(welcome_subject, welcome_message, from_email,
                  returning_accounts, fail_silently=False)

    # loop through the list of emails and passwords and create accounts for TA's
    index = 0
    for account in new_accounts:
        get_user_model().objects.create_user(account, passwords[index])
        index += 1

    messages.success(request, 'Success!')
    return redirect('lo_home')
