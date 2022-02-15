"""URL management for Teaching Assistant app."""
from django.urls import path, include
from . import views

urlpatterns = [
    # 'ta' prefix = teaching assistant
    path('', views.ta_home, name='ta_home'),
    path('account/', views.ta_account, name='ta_account'),
    path('ta_info', views.ta_info, name='ta_info'),
]
