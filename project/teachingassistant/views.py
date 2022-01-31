from django.shortcuts import render

def home(request):
    if request.user.is_authenticated:
        context = {
            'username' : request.user.username,
            'fname' : request.user.first_name,            
        }
        return render(request, 'teachingassistant/dashboard.html', context)
    return redirect('authentication/')
