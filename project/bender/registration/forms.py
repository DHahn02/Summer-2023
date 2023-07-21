from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from registration.models import UserProfile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=25, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=False, label="Last Name")

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]


class UserProfileForm(forms.ModelForm):
    birthdate = forms.CharField(widget=forms.TextInput(attrs={'type': 'date'}))
    mlb = forms.ChoiceField(label="Favorite MLB Team", choices=UserProfile.MLB.choices, required=False)
    nfl = forms.ChoiceField(label="Favorite NFL Team", choices=UserProfile.NFL.choices, required=False)
    nhl = forms.ChoiceField(label="Favorite NHL Team", choices=UserProfile.NHL.choices, required=False)
    nba = forms.ChoiceField(label="Favorite NBA Team", choices=UserProfile.NBA.choices, required=False)

    class Meta:
        model = UserProfile
        fields = ['birthdate', 'gender', 'nfl', 'mlb', 'nba', 'nhl']
