from django.contrib import admin

from .models import Jurisdiction, Entity, Location, Meeting


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'city',)
    list_editable = ('address', 'city',)
    list_filter = ('city',)


class MeetingAdmin(admin.ModelAdmin):
    # https://stackoverflow.com/questions/43390140/django-disallowedmodeladminlookup-for-lookup-in-admin-list-filter/44665384#44665384
    list_display = ('__str__', 'start', 'created',)
    list_editable = ('start',)
    list_filter = ('event_relation__event__creator__username',)


class EntityAdmin(admin.ModelAdmin):
    # https://stackoverflow.com/questions/43390140/django-disallowedmodeladminlookup-for-lookup-in-admin-list-filter/44665384#44665384
    list_display = ('name', 'owner', 'jurisdiction',)
    list_editable = ('owner', 'jurisdiction',)
    list_filter = ('owner__username',)
    ordering = ('name',)


admin.site.register(Jurisdiction)
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(Location, LocationAdmin)
