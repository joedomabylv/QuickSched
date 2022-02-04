"""View management for EmailUpload app. 'eu' prefix = email upload."""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage


def eu_upload(request):
    """Home route, only uploading emails."""
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        #print(uploaded_file.name)
        #print(uploaded_file.size)
        fs = FileSystemStorage()
        fs.save(uploaded_file.name, uploaded_file)
    return render(request, 'emailupload/ta_add.html')
