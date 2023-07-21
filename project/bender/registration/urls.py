from django.urls import path

from . import views

urlpatterns = [
    path("profile/", views.profile, name="profile"),
    path("create/", views.register, name="register"),
    path("set_profile/", views.profile_setup, name="profile_setup"),
]