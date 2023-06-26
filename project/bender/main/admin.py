from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Venue)
admin.site.register(Event)
admin.site.register(Performer)
admin.site.register(Team)
admin.site.register(TicketPack)
admin.site.register(Ticket)
