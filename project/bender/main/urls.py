from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path("home/", views.home, name='home'),
    path("sell/", views.create, name="create"),
    path("management/", views.management, name="management"),
    path("search/", views.search_results, name="search"),
    path("event/<slug:id>/", views.event_view, name="event"),
    path("team/<slug:id>/", views.team_view, name="team"),
    path("performer/<slug:id>/", views.performer_view, name="performer"),
    path("sell/", views.sell, name="sell"),
    path("sell/team/<slug:id>/", views.team_view, name="team_sell"),
    path("sell/performer/<slug:id>", views.performer_view, name="performer_sell"),
    path("sell/event/<slug:id>/", views.sell_tickets, name="sell-tickets"),
    path("buy/<slug:id>/", views.buy, name="buy"),
    path("success/<slug:id>/", views.success, name="success"),
    path("ticket_list/", views.ticket_list, name="ticket_list"),
    path("edit_ticket/<slug:id>/", views.edit_ticket, name="edit_ticket"),
]
