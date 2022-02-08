"""Views for TeachingAssistant App."""
from django.shortcuts import render, redirect
from .forms import NewTAForm, NewTAAvailabilityForm


def ta_home(request):
    """Directs the user to the TA dashboard."""
    # check if the user is authenticated before taking them to their homepage
    if request.user.is_authenticated:
        return render(request, 'teachingassistant/dashboard.html')

    # if they're not authenticated, take them to the login page
    return redirect('authentication/')


def ta_account(request):
    """Directs the user to their TA account status page."""
    # if the TA has a hold that needs information updated, direct them
    # with the proper form
    context = {
        'title_tag': request.user.first_name + ' ' + request.user.last_name,
        'new_ta_form': NewTAForm(),
        'new_ta_availability_form': NewTAAvailabilityForm(),
        }
    return render(request, 'teachingassistant/new_ta.html', context)
