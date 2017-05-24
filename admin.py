from django.contrib import admin

from .models import Jurisdiction, Entity, Location, Meeting


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'city',)
    list_editable = ('address', 'city',)
    list_filter = ('city',)


class MeetingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'start', 'created',)
    list_editable = ('start',)


class EntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'jurisdiction',)
    list_editable = ('owner', 'jurisdiction',)
    ordering = ('name',)


admin.site.register(Jurisdiction)
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(Location, LocationAdmin)
