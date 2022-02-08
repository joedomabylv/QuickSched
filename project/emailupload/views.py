"""View management for EmailUpload app. 'eu' prefix = email upload."""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage, default_storage
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
import csv
import os


def eu_upload(request):
    """Home route, only uploading emails."""
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        f = default_storage.open(os.path.join('', name), 'r')
        emails = []
        passwords = []
        file_reader = csv.reader(f, delimiter=',')
        for row in file_reader:
            emails = emails + row
        for email in emails:
            passwords.append(get_random_string(12))

        # loop through the list of emails and passwords
        # NEED TO ADD CHECKS TO AVOID CREATING DUPLICATE ACCOUNTS, IT CRASHES DJANGO ANYWAY
        index = 0
        while index < len(emails):
            print(f'{emails[index]}:{passwords[index]}')
            get_user_model().objects.create_user(emails[index], passwords[index])
            index += 1

    return render(request, 'emailupload/ta_add.html')
