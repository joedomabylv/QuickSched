"""Views for TeachingAssistant App."""
from django.shortcuts import render, redirect
from .forms import NewTAForm, NewTAAvailabilityForm
from .models import TA, Availability, Holds


def ta_home(request):
    """Directs the user to the TA dashboard."""
    context = {}

    # check if the user is authenticated before taking them to their homepage
    if request.user.is_authenticated:
        # get any holds on a TA's account
        all_holds = Holds.objects.all()
        for holds in all_holds:
            if holds.ta.student_id == request.user.ta_object.student_id:
                holds_list = []
                for hold in holds._meta.get_fields():
                    holds_list.append(hold.name)
                context['holds'] = holds_list
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
        # get general TA info
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        student_id = request.POST['student_id']
        experience = request.POST['experience']
        year = request.POST['year']
        default_time = '12:00'

        new_ta = TA.objects.create(
            first_name=first_name,
            last_name=last_name,
            student_id=student_id,
            experience=experience,
            # do we want the LO to determine whether or not a TA is contracted?
            contracted=False,
            year=year,
        )

        # create a new availability object
        availability_object = Availability.objects.create(
            monday_start=request.POST.get('monday_start', default_time),
            monday_end=request.POST.get('monday_end', default_time),
            tuesday_start=request.POST.get('tuesday_start', default_time),
            tuesday_end=request.POST.get('tuesday_end', default_time),
            wednesday_start=request.POST.get('wednesday_start', default_time),
            wednesday_end=request.POST.get('wednesday_end', default_time),
            thursday_start=request.POST.get('thursday_start', default_time),
            thursday_end=request.POST.get('thursday_end', default_time),
            friday_start=request.POST.get('friday_start', default_time),
            friday_end=request.POST.get('friday_end', default_time),
            saturday_start=request.POST.get('saturday_start', default_time),
            saturday_end=request.POST.get('saturday_end', default_time),
            sunday_start=request.POST.get('sunday_start', default_time),
            sunday_end=request.POST.get('sunday_end', default_time),
            ta=new_ta,
            )

        # create default holds object
        holds_object = Holds.objects.create(ta=new_ta)

        # assign the new TA object to the user model
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.ta_object = new_ta
        request.user.save()

        context = {
            'first_name': request.user.first_name,
        }
        print(request.user.first_name)

        return render(request, 'teachingassistant/new_ta_success.html', context)

    return redirect('authentication/sign_in')
