# https://docs.djangoproject.com/en/1.10/topics/class-based-views/generic-editing/#s-models-and-request-user
# http://django.cowhite.com/blog/adding-and-editing-model-objects-using-django-class-based-views-and-forms/
from braces.views import LoginRequiredMixin

from django.views.generic import CreateView, UpdateView, DetailView, ListView
from schedule.models import Calendar, Event, EventRelation
from schedule.periods import Period
from .forms import MeetingCreateViewForm
from .models import Jurisdiction, Meeting

import datetime
import operator


class SchedulerSavingMixin(object):
    def form_valid(self, form):
        meeting = form.save()
        end = meeting.start + datetime.timedelta(minutes=119)
        event = Event(
            start=meeting.start,
            end=end,
            title='{0} meeting'.format(meeting.entity.name),
            description=meeting.agenda,
            creator=self.request.user,
        )
        event.save()
        er = EventRelation.objects.create_relation(event, meeting)
        cal = Calendar.objects.get(name='civic')
        cal.events.add(event)
        return super(SchedulerSavingMixin, self).form_valid(form)


class MeetingCreateView(LoginRequiredMixin, CreateView):
    model = Meeting
    fields = '__all__'
#     form_class = MeetingCreateViewForm

    def form_valid(self, form):
        meeting = form.save()
        end = meeting.start + datetime.timedelta(minutes=119)
        event = Event(
            start=meeting.start,
            end=end,
            title='{0} meeting'.format(meeting.entity.name),
            description=meeting.agenda,
            creator=self.request.user,
        )
        event.save()
        er = EventRelation.objects.create_relation(event, meeting)
        er.save()
        cal = Calendar.objects.get(name='civic')
        cal.events.add(event)
        return super(MeetingCreateView, self).form_valid(form)

class MeetingUpdateView(LoginRequiredMixin, UpdateView):
    model = Meeting
    fields = '__all__'


class MeetingListView(LoginRequiredMixin, ListView):
    '''
    For entities to see a list of their own meetings.
    '''
    queryset = Meeting.objects.filter()


class MeetingDetailView(LoginRequiredMixin, DetailView):
    model = Meeting
    fields = '__all__'

# def today_and_tomorrow():
#     return datetime.datetime.today()
#     # today_and_tomorrow = datetime.datetime(2016,6,21)


class OccurrenceListView(ListView):
    '''
    For creating the print/online meetings list
    '''
    context_object_name = 'event_relation_list'
    template_name = 'civic_calendar/occurrence_list.html'
    # model = EventRelation

    # Add relevant Jurisdictions to response context
    def get_queryset(self):
        today_and_tomorrow = datetime.datetime.today()
        my_events = Event.objects.all()
        upcoming = Period(my_events, today_and_tomorrow, today_and_tomorrow+datetime.timedelta(days=2))
        occurrence_list = upcoming.get_occurrences()
        event_list = [ occurrence.event for occurrence in occurrence_list ]
        # figure out an order_by based on content_object.entity.jurisdiction.name
        # Can't
        # But! ...
        # ordered = sorted(queryset, key=operator.attrgetter('content_object.entity.jurisdiction.name'))
        # http://stackoverflow.com/questions/2412770/good-ways-to-sort-a-queryset-django
        queryset = EventRelation.objects.prefetch_related('content_object__entity__jurisdiction').filter(event_id__in=event_list)
        ordered = sorted(queryset, key=operator.attrgetter('content_object.entity.jurisdiction.name', 'event.start'))
        return ordered

    # def get_context_data(self):
    #     jurisdiction_set = set()
    #     for jurisdiction in queryset:
    #         jurisdiction_set.add(jurisdiction.content_object.entity.jurisdiction)
    #     jurisdiction_list = list(jurisdiction_set)
    #     context = super(OccurrenceListView, self).get_context_data(**kwargs)
    #     context['jurisdiction_list'] = jurisdiction_list
    #     return context
