from braces.views import LoginRequiredMixin

from django.views.generic import CreateView, UpdateView, DetailView, ListView
from schedule.models import Calendar, Event, EventRelation
from schedule.periods import Period
from .models import Jurisdiction, Meeting

import datetime


class MeetingCreateView(LoginRequiredMixin, CreateView):
    model = Meeting
    fields = '__all__'


class MeetingUpdateView(LoginRequiredMixin, UpdateView):
    model = Meeting
    fields = '__all__'


class MeetingDetailView(LoginRequiredMixin, DetailView):
    model = Meeting
    fields = '__all__'


class OccurrenceListView(ListView):
    context_object_name = 'occurrence_list'
    template_name = 'civic_calendar/occurrence_list.html'
    today_and_tomorrow = datetime.datetime.today()
    # today_and_tomorrow = datetime.datetime(2016,6,21)
    my_events = Event.objects.all()
    upcoming = Period(my_events, today_and_tomorrow, today_and_tomorrow+datetime.timedelta(days=2))
    occurrence_list = upcoming.get_occurrences()
    event_list = [ occurrence.event for occurrence in occurrence_list ]

    # queryset = EventRelation.objects.select_related('content_type').filter(event_id__in=event_list)
    queryset = EventRelation.objects.prefetch_related('content_object__entity__jurisdiction').filter(event_id__in=event_list)

    jurisdiction_set = set()
    for jurisdiction in queryset:
        jurisdiction_set.add(jurisdiction.content_object.entity.jurisdiction)
    jurisdiction_list = list(jurisdiction_set)

    # Add relevant Jurisdictions to response context
    def get_context_data(self, **kwargs):
        context = super(OccurrenceListView, self).get_context_data(**kwargs)
        context['jurisdiction_list'] = self.jurisdiction_list
        return context
    
