import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.
class Venue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20)
    location_name = models.CharField(max_length=30)
    stadium = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True)
    full_name = location_name.__str__() + name.__str__()

    def __str__(self):
        return self.location_name + " " + self.name


class Performer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home", null=True, blank=True)
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away", null=True, blank=True)
    performer = models.ForeignKey(Performer, on_delete=models.CASCADE, null=True, blank=True)

    class Leagues(models.TextChoices):
        MLB = "MLB", "MLB"
        NHL = "NHL", "NHL"
        NFL = "NFL", "NFL"
        NBA = "NBA", "NBA"

    # league = models.CharField(choices=Leagues.choices, null=True, blank=True, default=None, max_length=20)
    date = models.DateTimeField()
    location = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        if self.performer is None:
            return self.team1.name + " vs " + self.team2.name + " at " + self.location.name + ". " + self.date.date().__str__()
        else:
            return self.performer.name + " at " + self.location.name + ". " + self.date.date().__str__()


class TicketPack(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ticketpack")
    amount = models.PositiveIntegerField(validators=[MaxValueValidator(12)])
    price = models.IntegerField()
    section = models.IntegerField()
    row = models.IntegerField()
    for_sale = models.BooleanField(default=True)
    in_cart = models.BooleanField(default=False)
    divisible = models.BooleanField(default=True)

    def __str__(self):
        return self.user.first_name + "'s Group"


class Ticket(models.Model):
    class Delivery(models.TextChoices):
        PDF = 'PDF', "PDF Ticket"
        ELEC = 'ELEC', "Electronic Transfer"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(TicketPack, on_delete=models.CASCADE)
    game = models.ForeignKey(Event, on_delete=models.CASCADE)
    section = models.IntegerField()
    row = models.IntegerField()
    seat = models.IntegerField()
    price = models.IntegerField()
    method = models.CharField(choices=Delivery.choices, max_length=20)
    for_sale = models.BooleanField(default=True)
    in_cart = models.BooleanField(default=False)
    time_reserved = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.first_name + "'s Ticket: Section " + str(self.section) + " Row " + str(self.row) + \
            " Seat " + str(self.seat)
