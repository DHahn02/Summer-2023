from django import forms
from django.forms import ModelForm
from .models import *


class AddTicket(forms.Form):
    number_of_tickets = forms.ChoiceField(choices=((2, 2), (3, 3), (4, 4), (5, 5), (6, 6)))
    section = forms.IntegerField()
    row = forms.IntegerField()
    seat_start = forms.IntegerField(label="First Seat")
    seat_end = forms.IntegerField(label="Last Seat")
    delivery_method = forms.CharField(widget=forms.RadioSelect(choices=((1, "Electronic Transfer"), (2, "PDF Ticket"))))

    price_per_ticket = forms.IntegerField()

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('seat_start')
        end = cleaned_data.get('seat_end')
        t_num = cleaned_data.get('number_of_tickets')
        if str(abs(end - start) + 1) != str(t_num):
            raise ValidationError("Please enter the correct seats or correct amount of tickets")

    class Meta:
        model = Ticket
        fields = ['number_of_tickets', 'section', 'row', 'seat_start', 'seat_end', 'delivery_method', 'price_per_ticket']


class NewEvent(forms.Form):
    team_1 = forms.ModelChoiceField(label='Home Team', required=False, queryset=Team.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    team_2 = forms.ModelChoiceField(label='Away Team', required=False, queryset=Team.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    performer = forms.ModelChoiceField(required=False, queryset=Performer.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    location = forms.ModelChoiceField(required=True, queryset=Venue.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    date = forms.CharField(widget=forms.TextInput(attrs={'type': 'date'}))
    time = forms.CharField(widget=forms.TextInput(attrs={'type': 'time'}))

    def clean(self):
        cleaned_data = super().clean()
        home = cleaned_data.get("team_1")
        away = cleaned_data.get("team_2")
        performer = cleaned_data.get("performer")

        if home == away and home:
            raise ValidationError("A team cannot play themselves")
        if (home or away) and performer:
            raise ValidationError("A performer and a team cannot play together")
        if home and away is None:
            raise ValidationError("Two teams must be playing")

    class Meta:
        model = Event
        fields = ['team1', 'team2', 'performer', 'location', 'date', 'time']


class NewTeam(forms.Form):
    team_name = forms.CharField(label="Team Name")
    location = forms.CharField()
    stadium = forms.ModelChoiceField(queryset=Venue.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Team
        fields = ['team_name', 'location', 'stadium']


class NewPerformer(forms.Form):
    name = forms.CharField()

    class Meta:
        model = Performer
        fields = ['name']


class NewVenue(forms.Form):
    name = forms.CharField()
    location = forms.CharField()

    class Meta:
        model = Venue
        fields = ['name', 'location']


class EditTicketForm(forms.Form):
    price = forms.IntegerField(label="Price (USD. Applies to all tickets in group)")
    for_sale = forms.BooleanField(label="For Sale", required=False)

    class Meta:
        model = Ticket
        fields = ['price', 'for_sale']

