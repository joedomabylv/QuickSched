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
from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token


def home(request):
    """Route the user to the home sign in page."""
    return render(request, "authentication/sign_in.html")


def change_password(request):
    """
    Route user to the change_password page.

    If this is the users' first time logging in, guide them through
    changing their password.
    """
    return render(request, 'authentication/change_password.html')


def sign_up(request):
    """Handle new user (TA) sign ups."""
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('home')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('home')

        if len(username) > 20:
            messages.error(request, "Username must be under 20 charcters!!")
            return redirect('home')

        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('home')

        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('home')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()
        messages.success(request, "Your Account has been created succesfully!! Please check your email to confirm your email address in order to activate your account.")

        # Welcome Email
        subject = "Welcome to Quicksched- Django Login!!"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to Quicksched!! \nThank you for visiting our website!\n We have also sent you a confirmation email, please confirm your email address. \n\nThank You,\nQuicksched Guys"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirm your Email @ Quicksched - Django Login!!"
        message2 = render_to_string('email_confirmation.html',{

            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()

        return redirect('sign_in')

    return render(request, "authentication/sign_up.html")


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


def signin(request):
    """Sign the user in and direct them to the applicable dashboard."""
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']

        """
            This only authenticates when the user enters their actual username,
            which might be different than their email. JOE changed the input
            form in sign_in.html to allow non-emails
        """
        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            # direct user based on account status
            if user.is_superuser:
                return redirect('laborganizer/')
            else:
                return redirect('teachingassistant/')
        else:
            return redirect('sign_in')

    return render(request, "authentication/sign_in.html")


def sign_out(request):
    """Sign the user out of the application of direct them to the homepage."""
    logout(request)
    return redirect('sign_in')
