from django.shortcuts import render

def home(request):
    return render(request, 'teachingassistant/dashboard.html')
