"""Views for TeachingAssistant App."""
from django.shortcuts import render, redirect


def ta_home(request):
    """Directs the user to the TA dashboard."""
    # check if the user is authenticated before taking them to their homepage
    if request.user.is_authenticated:
        return render(request, 'teachingassistant/dashboard.html')

    # if they're not authenticated, take them to the login page
    return redirect('authentication/')


def ta_account(request):
    """Directs the user to their TA account status page."""
    # check if the user is authenticated before displaying personal information
    if request.user.is_authenticated:
        return render(request, 'teachingassistant/account.html')

    # if they're not authenticated, return them to the login page
    return redirect('authentication/')
