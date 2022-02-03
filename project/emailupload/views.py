"""View management for EmailUpload app. 'eu' prefix = email upload."""
from django.shortcuts import render


def eu_upload(request):
    """Home route, only uploading emails."""
    return render(request, 'emailupload/ta_add.html')
