from django.contrib import admin

from .models import Jurisdiction, Entity, Location, Meeting


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'city',)
    list_editable = ('address', 'city',)
    list_filter = ('city',)


class MeetingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'start', 'created',)
    list_editable = ('start',)


class UserAlphaSort(admin.SimpleListFilter):
    # https://stackoverflow.com/questions/16560055/django-admin-sorting-list-filter
    title = 'owner'
    parameter_name = 'owner'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        return [(i, j) for i, j in qs.values_list('owner', 'owner__username') \
            .distinct().order_by('owner__username')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(owner__exact=self.value())


class EntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'jurisdiction',)
    list_editable = ('owner', 'jurisdiction',)
    list_filter = (UserAlphaSort,)
    ordering = ('name',)


admin.site.register(Jurisdiction)
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(Location, LocationAdmin)
