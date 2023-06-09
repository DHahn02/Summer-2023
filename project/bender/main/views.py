from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .forms import *
from django.utils import timezone


# Create your views here.
def index(response, id):
    ls = Event.objects.get(id=id)

    if ls not in response.user.todolist.all():
        return render(response, "main/view.html", {})

    if response.method == "POST":
        if response.POST.get("save"):
            for item in ls.item_set.all():
                if response.POST.get("c" + str(item.id)) == "clicked":
                    item.complete = True
                else:
                    item.complete = False
                item.save()
        elif response.POST.get("newItem"):
            txt = response.POST.get("new")
            if len(txt) > 2:
                ls.item_set.create(text=txt, complete=False)
            else:
                print("Invalid input")
    return render(response, "main/list.html", {"game": ls})


def create(response):
    # response.user
    if response.method == "POST":
        form = AddTicket(response.POST)
        if form.is_valid():
            n = form.cleaned_data["name"]
            t = Event(name=n)
            t.save()
            response.user.todolist.add(t)
            return HttpResponseRedirect("/%i" % t.id)
    else:
        form = AddTicket()
    return render(response, "main/create.html", {"form": form})


def management(response):
    if not response.user.is_superuser:
        return HttpResponseRedirect("/")
    if response.method == "POST":
        venue_form = NewVenue(response.POST, prefix="venue")
        performer_form = NewPerformer(response.POST, prefix="performer")
        team_form = NewTeam(response.POST, prefix="team")
        event_form = NewEvent(response.POST, prefix="event")
        if venue_form.is_valid():
            name = venue_form.cleaned_data['name']
            location = venue_form.cleaned_data['location']
            venue = Venue(name=name, location=location)
            venue.save()
            venue.event_set.create()
            return HttpResponseRedirect("/management")
        if performer_form.is_valid():
            name = performer_form.cleaned_data['name']
            performer = Performer(name=name)
            performer.save()
            performer.event_set.create()
            return HttpResponseRedirect("/management")
        if team_form.is_valid():
            name = team_form.cleaned_data['team_name']
            location = team_form.cleaned_data['location']
            stadium = team_form.cleaned_data['stadium']
            team = Team(name=name, location_name=location, stadium=stadium)
            team.save()
            return HttpResponseRedirect("/management")
        if event_form.is_valid():
            team1 = event_form.cleaned_data['team_1']
            team2 = event_form.cleaned_data['team_2']
            performer = event_form.cleaned_data['performer']
            location = event_form.cleaned_data['location']
            date = event_form.cleaned_data['date']
            time = event_form.cleaned_data['time']
            event = Event(team1=team1, team2=team2, performer=performer, date=date + " " + time, location=location)
            event.save()
            if performer is None:
                team1.home.add(event)
                team2.away.add(event)
            else:
                performer.event_set.add(event)
            location.event_set.add(event)

            return HttpResponseRedirect("/management")
    else:
        venue_form = NewVenue(prefix="venue")
        performer_form = NewPerformer(prefix="performer")
        team_form = NewTeam(prefix="team")
        event_form = NewEvent(prefix="event")
    return render(response, "main/management.html",
                  {"venue_form": venue_form, "performer_form": performer_form, "team_form": team_form,
                   "event_form": event_form, "events": Event.objects.all()})


def view(response):
    return render(response, "main/view.html", {})


def home(response):
    events = Event.objects.all()
    teams = Team.objects.all()
    performers = Performer.objects.all()
    return render(response, "main/home.html", {"events": events, "teams": teams, "performers": performers})


def event_view(request, id):
    event = Event.objects.get(id=id)
    ticketpacks = event.ticketpack_set.all()
    available = {}
    for ticketpack in ticketpacks:
        num_available = 0
        tickets = ticketpack.ticket_set.all()
        for ticket in tickets:
            if ticket.user == ticketpack.user and ticket.for_sale and not ticket.in_cart:
                num_available += 1
            available[ticketpack] = num_available
    return render(request, 'main/event.html', {"event": event, "ticketpacks": ticketpacks, "available": available})


def team_view(request, id):
    url = request.get_full_path()
    if "sell" in url:
        path = "/sell/"
    else:
        path = "/"
    team = Team.objects.get(id=id)
    games = []
    for game in team.home.all().order_by('date'):
        if game.date > timezone.now():
            games.append(game)
    for game in team.away.all().order_by('date'):
        if game.date > timezone.now():
            games.append(game)
    games.sort(key=sortDate)
    return render(request, 'main/team.html', {"team": team, "games": games, "path": path})


# use for sorting the home and away games in order, not all home first
def sortDate(game):
    return game.date


def performer_view(request, id):
    url = request.get_full_path()
    if "sell" in url:
        path = "/sell/"
    else:
        path = "/"
    performer = Performer.objects.get(id=id)
    fut_events = []
    events = performer.event_set.all().order_by('date')
    for event in events:
        if event.date > timezone.now():
            fut_events.append(event)
    return render(request, 'main/performer.html', {"performer": performer, "events": fut_events, "path": path})


def sell(request):
    return render(request, 'main/create.html', {})


def buy(request, id):
    ticketpack = TicketPack.objects.get(id=id)
    tickets = ticketpack.ticket_set.all()
    if len(tickets) == 1:
        return HttpResponseRedirect("/failure")
    ticket = tickets[len(tickets)-1]
    ticket.in_cart = True
    ticket.for_sale = False
    ticket.time_reserved = timezone.now()
    ticket.save()
    return render(request, 'main/checkout.html', {"ticket": ticket, "tax": ticket.price * 0.075, "total": ticket.price*1.075})


def sell_tickets(request, id):
    if request.method == 'POST':
        form = AddTicket(request.POST)
        if form.is_valid():
            event = Event.objects.get(id=id)
            amount = int(form.cleaned_data['number_of_tickets'])
            section = form.cleaned_data['section']
            row = form.cleaned_data['row']
            start = form.cleaned_data['seat_start']
            end = form.cleaned_data['seat_end']
            method = form.cleaned_data['delivery_method']
            price = form.cleaned_data['price_per_ticket']
            pack = TicketPack(game=event, user=request.user, amount=amount, price=price, section=section, row=row)
            pack.save()
            if method == "1":
                for i in range(0, amount):
                    print(pack)
                    ticket = Ticket(user=request.user, group=pack, game=event, section=section, row=row, seat=start+i, price=price, method=Ticket.Delivery.ELEC)
                    if i == 0:
                        ticket.for_sale = False
                    ticket.save()
            else:
                for i in range(0, amount):
                    ticket = Ticket(user=request.user, group=pack, game=event, section=section, row=row, seat=start + i,
                                    price=price, method=Ticket.Delivery.PDF)
                    if i == 0:
                        ticket.for_sale = False
                    ticket.save()
            return HttpResponseRedirect("/sell")
    else:
        form = AddTicket()
    event = Event.objects.get(id=id)
    return render(request, 'main/tickets.html', {"form": form, "event": event})


def search_results(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        res = None
        term = request.POST.get("event")
        events = []
        teams = []
        performers = []
        if term:
            for event in Event.objects.all():
                if event.team1 and event.team1.name.lower().startswith(term.lower()) or not (
                        not event.team2 or not event.team2.name.lower().startswith(
                        term.lower())) or event.performer and event.performer.name.lower().startswith(term.lower()):
                    if event.date > timezone.now():
                        events.append(event)
            for team in Team.objects.all():
                if team.name.lower().startswith(term.lower()):
                    teams.append(team)
            for performer in Performer.objects.all():
                if performer.name.lower().startswith(term.lower()):
                    performers.append(performer)
        if (len(events) > 0 or len(teams) > 0 or len(performers) > 0) and len(term) > 0:
            data = []
            for team in teams:
                item = {
                    "key": team.id,
                    "name": team.name,
                    "location": team.location_name
                }
                data.append(item)
            for performer in performers:
                item = {
                    "key": performer.id,
                    "name": performer.name
                }
                data.append(item)
            events.sort(key=sortDate)

            if len(data) <= 8:
                for event in events:
                    if len(data) <= 8:
                        item = {
                            "key": event.id,
                            "name": event.__str__(),
                            "team1": event.team1.__str__(),
                            "team2": event.team2.__str__(),
                            "date": event.date.__str__(),
                            "location": event.location.name,
                        }
                        data.append(item)
            res = data
        else:
            res = "No results found"
        return JsonResponse({'data': res})
    return JsonResponse({})
