"""Views for TeachingAssistant App."""
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Availability, Holds
from laborganizer.models import AllowTAEdit
from django.contrib.auth.decorators import login_required
from teachingassistant.ta_utils import (parse_availability,
                                        validate_student_id)
from laborganizer.lo_utils import (get_current_semester)


@login_required
def ta_home(request):
    """Directs the user to the TA dashboard."""
    # check if the user is a superuser
    if not request.user.is_superuser:
        # get the TA object assigned to the current user
        ta = request.user.ta_object

        # get any holds on a TA's account
        holds = Holds.objects.get(pk=ta.holds_key)

        # get any labs the TA is assigned to for the current semester
        semester = get_current_semester()
        labs = ta.get_assigned_labs(semester)

        context = {
            'ta': ta,
            'holds': holds,
            'semester': semester,
            'labs': labs,
        }

        return render(request, 'teachingassistant/dashboard.html', context)

    # the user is a superuser, take them back to the login page
    return redirect('sign_in')


@login_required
def ta_account(request):
    """
    Directs the user to their TA account status page.

    If the TA has a hold that requires them to edit their information or
    the LO has allowed it, they will be directed to the account page. If not,
    they will be shown that they don't have permission to edit their
    information.
    """
    # check if the user is a superuser
    if not request.user.is_superuser:
        # get holds for current ta
        ta_holds_key = request.user.ta_object.holds_key
        holds_object = Holds.objects.get(pk=ta_holds_key)

        # get the AllowTAEdit object and check if the LO has allowed TA's to
        # edit their information
        allow_object = AllowTAEdit.objects.all()[0]

        if holds_object.incomplete_profile or allow_object.is_allowed():
            context = {
                'title_tag': request.user.first_name + ' ' + request.user.last_name,
                'ta': request.user.ta_object,
            }
            return render(request, 'teachingassistant/account/account.html', context)

        messages.warning(request, 'You\'re not allowed to edit your information! Please contact your course organizer.')
        return redirect('ta_home')

    # the user is a superuser, take them back to the login page
    return redirect('sign_in')


@login_required
def ta_info(request):
    """Update TA mation via POST form."""
    # check if the user is a superuser
    if not request.user.is_superuser:
        if request.method == 'POST':
            # set variables
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            student_id = request.POST['student_id']
            experience = request.POST['experience']
            year = request.POST['year']
            number_of_classes = int(request.POST.get('submit_button'))

            if not validate_student_id(student_id, request.user.ta_object):
                messages.error(request, 'It looks like an account already exists with your student ID... Please contact your lab organizer')
                return redirect('ta_home')

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

            messages.success(request, 'Your information has been updated! Thank you!')
            return redirect('ta_home')

    # user is a superuser, take them back to the login page
    return redirect('sign_in')
