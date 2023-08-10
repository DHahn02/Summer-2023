import heapq

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from .forms import *
from django.utils import timezone
from django.core.mail import send_mail
from heapq import heappush, heappop, heapify


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
    if response.user.is_authenticated:
        name = response.user.first_name
    else:
        name = ""
    return render(response, "main/home.html", {"events": events, "teams": teams, "performers": performers, "first_name": name})


def event_view(request, id):
    event = Event.objects.get(id=id)
    ticketpacks = event.ticketpack_set.all()
    available = {}
    heap = []
    for ticketpack in ticketpacks:
        num_available = 0
        if ticketpack.user != request.user:
            tickets = ticketpack.ticket_set.all()
            for ticket in tickets:
                if ticket.user == ticketpack.user and ticket.for_sale and not ticket.in_cart:
                    num_available += 1
            available[ticketpack] = num_available  # if any issues, re-indent this line
            if num_available > 0 and request.user.is_authenticated:
                heapq.heappush(heap, (getScore(request.user, ticketpack.user, ticketpack.game), len(heap), ticketpack))
    heaped = [heapq.heappop(heap)[2] for _ in range(len(heap))]
    return render(request, 'main/event.html', {"user": request.user, "event": event, "ticketpacks": ticketpacks, "available": available, "alt_ticketpacks": heaped[::-1]})


def getScore(buyer, seller, event):
    score = 0
    bp = buyer.userprofile
    sp = seller.userprofile
    if bp.mlb == sp.mlb:
        score += 5
    if bp.nfl == sp.nfl:
        score += 5
    if bp.nhl == sp.nhl:
        score += 5
    if bp.nba == sp.nba:
        score += 5
    if bp.gender == sp.gender:
        score += 10
    if abs(getAge(bp.birthdate) - getAge(sp.birthdate)) <= 5:
        score += 3
    return score


def getAge(dob):
    return timezone.now().year - dob.year


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
    ticket = tickets[len(tickets) - 1]
    if not ticket.in_cart:
        ticket.in_cart = True
        ticket.for_sale = False
        ticket.time_reserved = timezone.now()
        ticket.save()
    time_left = (ticket.time_reserved + timezone.timedelta(minutes=15)) - timezone.now()
    time_left = int(time_left.total_seconds())
    if time_left <= 0 and not ticket.for_sale:
        ticket.in_cart = False
        ticket.for_sale = True
        ticket.time_reserved = None
        ticket.save()
    return render(request, 'main/checkout.html',
                  {"ticket": ticket, "tax": ticket.price * 0.075, "total": ticket.price * 1.075,
                   "time_remaining": time_left})


def success(request, id):
    ticket = Ticket.objects.get(id=id)
    ticket.for_sale = False
    ticket.user = request.user
    ticket.time_reserved = None
    ticket.save()
    send_mail("Your Receipt from Bender", "You spent " + str(ticket.price*1.075) + " on your ticket.", "shimmiedtest@gmail.com", [request.user.email], fail_silently=False,)
    return render(request, "main/success.html", {})


def ticket_list(request):
    all_tickets = request.user.ticket_set.all()
    for_sale_tickets = []
    sold_tickets = []
    bought_tickets = []
    for ticket in all_tickets:
        if ticket.group.user == request.user:
            if ticket.for_sale:
                for_sale_tickets.append(ticket)
            else:
                if ticket.user != request.user:
                    sold_tickets.append(ticket)
                else:
                    bought_tickets.append(ticket)
        else:
            bought_tickets.append(ticket)
    for pack in request.user.ticketpack.all():
        for ticket in pack.ticket_set.all():
            if ticket.user != request.user:
                sold_tickets.append(ticket)

    return render(request, "main/ticket_list.html", {"bought": bought_tickets, "sold": sold_tickets, "for_sale": for_sale_tickets})


def edit_ticket(request, id):
    ticket = Ticket.objects.get(id=id)
    if request.user == ticket.user and request.user == ticket.group.user:
        initial = {
            "price": ticket.price,
            "for_sale": ticket.for_sale,
        }
        if request.method == 'POST':
            form = EditTicketForm(request.POST, initial=initial)
            if form.is_valid():
                for_sale = form.cleaned_data['for_sale']
                price = form.cleaned_data['price']
                ticket_group = ticket.group
                ticket.for_sale = for_sale
                ticket.save()
                for t in ticket_group.ticket_set.all():
                    if t.for_sale:
                        t.price = price
                        t.save()
        else:
            form = EditTicketForm(initial=initial)
        return render(request, "main/ticketedit.html", {"form": form, "ticket": ticket})
    else:
        raise Http404


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
                    ticket = Ticket(user=request.user, group=pack, game=event, section=section, row=row, seat=start + i,
                                    price=price, method=Ticket.Delivery.ELEC)
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
