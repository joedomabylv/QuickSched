"""View management for LabOrganizer app. 'lo' prefix = lab organizer."""
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage


def lo_home(request):
    """Home route."""
    return render(request, 'laborganizer/dashboard.html')


def lo_ta_management(request):
    """TA Management route."""
    return render(request, 'laborganizer/ta_management.html')


def lo_ta_add(request):
    """View for LO to add new TA's to the roster."""
    return render(request, 'laborganizer/ta_add.html')


def lo_upload(request):
    """Upload route."""
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        fs.save(uploaded_file.name, uploaded_file)
    return render(request, 'laborganizer/dashboard.html')
