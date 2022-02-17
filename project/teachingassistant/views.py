"""Views for TeachingAssistant App."""
from django.shortcuts import render, redirect
from .forms import NewTAForm, NewTAAvailabilityForm
from .models import TA, Availability, Holds
from laborganizer.models import Lab


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
        labs_list = []
        for lab in all_labs:
            for ta in lab.assigned_tas.all():
                if ta.student_id == request.user.ta_object.student_id:
                    labs_list.append(lab)
                context['labs'] = labs_list
                print(labs_list)
        return render(request, 'teachingassistant/dashboard.html', context)

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


def ta_info(request):
    """Update TA mation via POST form."""
    if request.method == 'POST':
        # set variables
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        student_id = request.POST['student_id']
        experience = request.POST['experience']
        year = request.POST['year']

        # to be used in the event of improper datetime for Availability object
        default_time = '12:00'

        # gather keys
        availability_key = request.user.ta_object.availability_key
        holds_key = request.user.ta_object.holds_key

        # gather related objects (Holds, Availability)
        ta_availability = Availability.objects.get(id=availability_key)
        ta_holds = Holds.objects.get(id=holds_key)

        # update existing TA object
        request.user.ta_object.first_name = first_name
        request.user.ta_object.last_name = last_name
        request.user.ta_object.student_id = student_id
        request.user.ta_object.experience = experience
        request.user.ta_object.contraced = False
        request.user.ta_object.year = year

        ta_availability.monday_start = request.POST.get('monday_start',
                                                        default_time)
        ta_availability.monday_end = request.POST.get('monday_end',
                                                      default_time)
        ta_availability.tuesday_start = request.POST.get('tuesday_start',
                                                         default_time)
        ta_availability.tuesday_end = request.POST.get('tuesday_end',
                                                       default_time)
        ta_availability.wednesday_start = request.POST.get('wednesday_start',
                                                           default_time)
        ta_availability.wednesday_end = request.POST.get('wednesday_end',
                                                         default_time)
        ta_availability.thursday_start = request.POST.get('thurdsay_start',
                                                          default_time)
        ta_availability.thursday_end = request.POST.get('thursday_end',
                                                        default_time)
        ta_availability.friday_start = request.POST.get('friday_start',
                                                        default_time)
        ta_availability.friday_end = request.POST.get('friday_end',
                                                      default_time)
        ta_availability.saturday_start = request.POST.get('saturday_start',
                                                          default_time)
        ta_availability.saturday_end = request.POST.get('saturday_end',
                                                        default_time)
        ta_availability.sunday_start = request.POST.get('sunday_start',
                                                        default_time)
        ta_availability.sunday_end = request.POST.get('sunday_end',
                                                      default_time)

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
