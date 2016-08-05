from django.contrib import admin

from .models import Jurisdiction, Entity, Location, Meeting


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'city',)
    list_editable = ('address', 'city',)


class MeetingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'start',)
    list_editable = ('start',)


admin.site.register(Jurisdiction)
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Entity)
admin.site.register(Location, LocationAdmin)
