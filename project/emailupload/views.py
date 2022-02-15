"""View management for EmailUpload app. 'eu' prefix = email upload."""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage, default_storage
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.mail import EmailMessage, send_mail
from quicksched import settings
import csv
import os


def eu_upload(request):
    """Home route, only uploading emails."""
    if request.method == 'POST':

        # Snatch the uploaded document [NEED TO HAVE NGINX DO FILE HANDLING UPON DEPLOYMENT]
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()

        # Checks if there is an existing list of emails, then grabs the name
        old_emails_name=""
        existing_emails = False
        if len(default_storage.listdir('')[1]) >= 1:
            print("Old Email File Found")
            existing_emails = True
            old_emails_name = default_storage.listdir('')[1][0]

        # Saves the uploaded file to the default media directory, then initializes lists and file reader
        new_emails = fs.save(uploaded_file.name, uploaded_file)
        new_emails_file = default_storage.open(os.path.join('', new_emails), 'r')
        returning_accounts = []
        new_accounts = []
        new_emails = []
        old_emails = []
        passwords = []
        new_file_reader = csv.reader(new_emails_file, delimiter=',')

        # if there are any returning emails from a previous upload, make sure they are not prompted to make a new account
        if existing_emails:
            old_emails_file = default_storage.open(os.path.join('', old_emails_name), 'r')
            old_file_reader = csv.reader(old_emails_file, delimiter=',')

            for old_user in old_file_reader:
                old_emails = old_emails + old_user

            for new_user in new_file_reader:
                new_emails = new_emails + new_user

            for old_email in old_emails:
                if old_email in new_emails:
                    returning_accounts.append(old_email)

            for new_email in new_emails:
                if new_email not in returning_accounts:
                    new_accounts.append(new_email)

        else:
            for row in new_file_reader:
                new_accounts = new_accounts + row

        # Generate passwords for new emails
        for email in new_emails:
            passwords.append(get_random_string(12))

        # loop through the list of emails and passwords
        index = 0
        while index < len(new_accounts):
            username = new_accounts[index]
            temp_pass = passwords[index]
            print(f'{new_accounts[index]}:{passwords[index]}')
            get_user_model().objects.create_user(username, temp_pass)
            index += 1

        # Welcome Email
        if len(new_accounts) > 0:
            welcome_subject = "Welcome to Quicksched- Django Login!!"
            welcome_message = "Hello!! \n Welcome to Quicksched!!\nYour Account has successfully been created. \
            \n\n To finish your registration, please use your email and temporary password down below to login.\n \
            You will be prompted to change it upon your login.\n\n Temporary Password: " + temp_pass
            from_email = settings.EMAIL_HOST_USER
            send_mail(welcome_subject, welcome_message, from_email, new_accounts, fail_silently=True)

        if len(returning_accounts) > 0:
            welcome_subject = "Welcome to back to Quicksched!!"
            welcome_message = "Hello!\n This email is here to let you know that your email has been registered back in the system.\n\
            Please sign in and update your schedule and other information about your availability and qualifications."
            from_email = settings.EMAIL_HOST_USER
            send_mail(welcome_subject, welcome_message, from_email, returning_accounts, fail_silently=True)

        print("new accounts: " + str(new_accounts))
        print("returning accounts: " + str(returning_accounts))

        # delete the list of old emails
        if existing_emails:
            default_storage.delete(os.path.join('', old_emails_name))

    return render(request, 'emailupload/ta_add.html')
