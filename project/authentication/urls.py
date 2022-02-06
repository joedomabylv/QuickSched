from django.contrib import admin
from django.urls import path, include
from . import views
from .views import CustomPasswordChangeView

urlpatterns = [
    path('', views.home, name='home'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('ta_dashboard', views.ta_dashboard, name='ta_dashboard'),
    path('change_password', CustomPasswordChangeView.as_view(template_name="authentication/change_password.html"), name='change_password'),
    path('change_password_success', views.change_password_success,
         name='change_password_success'),
    path('sign_in', views.sign_in, name='sign_in'),
    path('sign_out', views.sign_out, name='sign_out'),
]
