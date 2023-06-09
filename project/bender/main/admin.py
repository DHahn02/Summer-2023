from django.contrib import admin
from .models import ToDoList, Item, Game, Team, TicketPack, Ticket

# Register your models here.
admin.site.register(ToDoList)
admin.site.register(Item)
admin.site.register(Game)
admin.site.register(Team)
admin.site.register(TicketPack)
admin.site.register(Ticket)
