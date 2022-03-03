"""Views for TeachingAssistant App."""
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import NewTAForm, NewTAAvailabilityForm
from .models import TA, Availability, Holds
from laborganizer.models import Lab, AllowTAEdit
from teachingassistant.ta_utils import (availability_list_to_tuples,
                                        parse_availability)


def ta_home(request):
    """Directs the user to the TA dashboard."""
    context = {}

    # check if the user is authenticated before taking them to their homepage
    if request.user.is_authenticated:
        # get any holds on a TA's account
        all_holds = Holds.objects.all()
        for holds in all_holds:
            # loop through all Holds objects, compare against the
            # student ID of the user
            if (holds.ta.student_id == request.user.ta_object.student_id or
                holds.ta.student_id is None):
                holds_list = []
                if holds.incomplete_profile:
                    holds_list.append('incomplete_profile')
                if holds.update_availability:
                    holds_list.append('update_availability')
                if holds.update_experience:
                    holds_list.append('update_experience')
                context['holds'] = holds_list

        # get all labs a TA is assigned to
        all_labs = Lab.objects.all()

        return render(request, 'teachingassistant/dashboard.html', context)

    # if they're not authenticated, take them to the login page
    return redirect('authentication/')


def ta_account(request):
    """
    Directs the user to their TA account status page.

    If the TA has a hold that requires them to edit their information or
    the LO has allowed it, they will be directed to the account page. If not,
    they will be shown that they don't have permission to edit their
    information.
    """
    # get holds for current ta
    ta_holds_key = request.user.ta_object.holds_key
    holds_object = Holds.objects.get(pk=ta_holds_key)

    # get the AllowTAEdit object and check if the LO has allowed TA's to
    # edit their information
    allow_object = AllowTAEdit.objects.get(pk=1)

    if holds_object.incomplete_profile or allow_object.is_allowed():
        context = {
            'title_tag': request.user.first_name + ' ' + request.user.last_name,
            'new_ta_form': NewTAForm(),
        }
        return render(request, 'teachingassistant/account/account.html', context)

    messages.warning(request, 'You\'re not allowed to edit your information!')
    return redirect('ta_home')


def ta_info(request):
    """Update TA mation via POST form."""
    if request.method == 'POST':
        # set variables
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        student_id = request.POST['student_id']
        experience = request.POST['experience']
        year = request.POST['year']
        number_of_classes = int(request.POST.get('submit_button'))

        # parse the input availability
        availability_list = parse_availability(request, number_of_classes)

        # gather keys
        availability_key = request.user.ta_object.availability_key
        holds_key = request.user.ta_object.holds_key

        # gather related objects (Holds, Availability)
        ta_availability = Availability.objects.get(id=availability_key)
        ta_holds = Holds.objects.get(id=holds_key)

        # update availability object
        ta_availability.edit_time(availability_list)

        # update existing TA object
        request.user.ta_object.first_name = first_name
        request.user.ta_object.last_name = last_name
        request.user.ta_object.student_id = student_id
        request.user.ta_object.experience = experience
        request.user.ta_object.contraced = False
        request.user.ta_object.year = year

        # TA info has been updated, remove hold
        if ta_holds.incomplete_profile:
            ta_holds.incomplete_profile = False

        # assign the new TA object to the user model
        request.user.first_name = first_name
        request.user.last_name = last_name

        # save all new changes to the database
        request.user.save()
        request.user.ta_object.save()
        ta_availability.save()
        ta_holds.save()

        context = {
            'first_name': request.user.first_name,
        }

        return render(request, 'teachingassistant/new_ta_success.html', context)

    return redirect('authentication/sign_in')
