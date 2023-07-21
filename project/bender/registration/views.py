from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from django.contrib.auth.models import User


# Create your views here.
def register(response):
    if response.method == "POST":
        form = RegistrationForm(response.POST)
        if form.is_valid():
            form.save()
        return redirect("/home")
    else:
        form = RegistrationForm
    return render(response, "registration/register.html", {"form":form})


def profile(request):
    return render(request, "registration/profile.html", {"name": request.user.first_name})


@login_required
def profile_setup(request):
    initial_data = {
        "birthdate": request.user.userprofile.birthdate,
        "gender": request.user.userprofile.gender,
        "mlb": request.user.userprofile.mlb,
        "nfl": request.user.userprofile.nfl,
        "nhl": request.user.userprofile.nhl,
        "nba": request.user.userprofile.nba
    }
    if request.method == 'POST':
        form = UserProfileForm(request.POST, initial=initial_data)
        if form.is_valid():
            profile = request.user.userprofile
            profile.gender = form.cleaned_data["gender"]
            profile.birthdate = form.cleaned_data["birthdate"]
            profile.nfl = form.cleaned_data["nfl"]
            profile.mlb = form.cleaned_data["mlb"]
            profile.nba = form.cleaned_data["nba"]
            profile.nhl = form.cleaned_data["nhl"]
            profile.save()
    else:
        form = UserProfileForm(initial=initial_data)
    return render(request, "registration/setup.html", {"p_form": form, "name": request.user.first_name})

# @login_required
# @transaction.atomic
# def profile_setup(request):
#     if request.method == 'POST':
#         user_form = RegistrationForm(request.POST, instance=request.user)
#         user_profile_form = UserProfileForm(request.POST, instance=request.user.userprofile)
#         if user_form.is_valid() and user_profile_form.is_valid():
#             user_form.save()
#             user_profile_form.save()
#             return HttpResponseRedirect("user:profile")
#     else:
#         user_form = RegistrationForm(instance=request.user)
#         user_profile_form = UserProfileForm(instance=request.user.userprofile)
#     return render(request, "registration/setup.html", {"u_form": user_form, "p_form": user_profile_form})