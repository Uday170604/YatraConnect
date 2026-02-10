from django.contrib import admin
from .models import Bus, BusStop, Seat, Meal, Booking

class BusStopInline(admin.TabularInline):
    model = BusStop
    extra = 1

class BusAdmin(admin.ModelAdmin):
    inlines = [BusStopInline]

admin.site.register(Bus, BusAdmin)
admin.site.register(Seat)
admin.site.register(Meal)
admin.site.register(Booking)
# admin.site.register(BusStop) # Already inlined in Bus
