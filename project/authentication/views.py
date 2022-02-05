"""Authentication app views."""
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from quicksched import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from . tokens import generate_token
from teachingassistant.models import TA, Availability


def home(request):
    """Route the user to the home sign in page."""
    return render(request, "authentication/sign_in.html")


def change_password(request):
    """
    Allow the user to change their password for the first time.

    After completion, send them to the dashboard.
    """
    # update the password and direct the TA to their dashboard, flip
    # the TA flag, i.e. request.user.init_changed_password = True
    return redirect('sign_in')


def sign_up(request):
    """Handle new user (TA) sign ups."""
    # somehow need to pass the user model into the account creation section
    if request.method == "POST":
        fname = request.POST['fname']
        lname = request.POST['lname']
        student_id = request.POST['student-id']
        experience = request.POST['experience']
        year = request.POST['year']

        # create a new availability object
        availability_object = Availability.objects.create(
            monday_start=request.POST['monday-start'],
            monday_end=request.POST['monday-end'],
            tuesday_start=request.POST['tuesday-start'],
            tuesday_end=request.POST['tuesday-end'],
            wednesday_start=request.POST['wednesday-start'],
            wednesday_end=request.POST['wednesday-end'],
            thursday_start=request.POST['thursday-start'],
            thursday_end=request.POST['thursday-end'],
            friday_start=request.POST['friday-start'],
            friday_end=request.POST['friday-end'],
            saturday_start=request.POST['saturday-start'],
            saturday_end=request.POST['saturday-end'],
            sunday_start=request.POST['sunday-start'],
            sunday_end=request.POST['sunday-end'],
            )

        # create a new TA object
        TA.objects.create(
            first_name=fname,
            last_name=lname,
            student_id=student_id,
            availability=availability_object,
            contracted=True,
            experience=experience,
            year=year
            )

        # sign the user in

        # direct them to their dashboard

    return render(request, "authentication/sign_in.html")


def activate(request, uidb64, token):
    """Activate a new user account."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request, myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('sign_in')
    else:
        return render(request, 'activation_failed.html')


def sign_in(request):
    """Sign the user in and direct them to the applicable dashboard."""
    if request.method == 'POST':
        email = request.POST['email']
        pass1 = request.POST['pass1']

        """
            This only authenticates when the user enters their actual username,
            which might be different than their email. JOE changed the input
            form in sign_in.html to allow non-emails
        """
        user = authenticate(email=email, password=pass1)

        if user is not None:
            login(request, user)
            # direct user based on account status
            if user.is_superuser:
                return redirect('laborganizer/')
            else:
                # check if the user has changed their password for the first time
                if not user.init_changed_password:
                    # send them to the change their password
                    # somehow figure out how to flip the flag after
                    # they've changed their password

                    # send them to the new user form afterwards
                    return render(request, "authentication/change_password.html")

                # else, take them to their dashboard
                print(user.email)
                return redirect('teachingassistant/')
        else:
            return redirect('sign_in')

    return render(request, "authentication/sign_in.html")


def sign_out(request):
    """Sign the user out of the application of direct them to the homepage."""
    logout(request)
    return redirect('sign_in')
