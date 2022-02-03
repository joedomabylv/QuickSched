from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('change_password/', views.change_password, name='change_password'),
    path('sign_in', views.signin, name='sign_in'),
    path('sign_out', views.sign_out, name='sign_out'),
]
