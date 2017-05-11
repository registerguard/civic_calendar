# https://docs.djangoproject.com/en/1.10/topics/class-based-views/generic-editing/#s-models-and-request-user
# http://django.cowhite.com/blog/adding-and-editing-model-objects-using-django-class-based-views-and-forms/
from braces.views import LoginRequiredMixin

from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.template import loader, Context, RequestContext, Template
from django.views.generic import CreateView, UpdateView, DetailView, ListView, \
    DeleteView
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
    form_class = MeetingCreateViewForm
    # if no success_url, defaults to model object get_absolute_url(), if
    # available https://docs.djangoproject.com/en/1.10/topics/class-based-views/generic-editing/#model-forms
    success_url = reverse_lazy('meeting-list')

    # passing request.user to MeetingCreateViewForm
    def get_form_kwargs(self):
        kwargs = super(MeetingCreateView, self).get_form_kwargs()
        kwargs.update({'owner': self.request.user})
        return kwargs

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
        try:
            cal = Calendar.objects.get(name='civic')
        except Calendar.DoesNotExist:
            error_msg = "Calendar object not found."
            raise Calendar.DoesNotExist(error_msg)
            
        cal.events.add(event)
        return super(MeetingCreateView, self).form_valid(form)

class MeetingUpdateView(LoginRequiredMixin, UpdateView):
    model = Meeting
    form_class = MeetingCreateViewForm
    success_url = reverse_lazy('meeting-list')

    def get_form_kwargs(self):
        kwargs = super(MeetingUpdateView, self).get_form_kwargs()
        kwargs.update({'owner': self.request.user})
        return kwargs

    def form_valid(self, form):
        er = EventRelation.objects.get(object_id=self.object.id)
        event = Event.objects.get(pk=er.event.id)
        event.start = form.instance.start
        event.end = form.instance.start + datetime.timedelta(minutes=119)
        event.description = form.instance.agenda
        event.save()
        return super(MeetingUpdateView, self).form_valid(form)

class MeetingListView(LoginRequiredMixin, ListView):
    '''
    For entities to see a list of their own meetings.
    '''
    login_url = reverse_lazy('login')
    template_name = 'civic_calendar/eventrelation_list.html'

    def get_queryset(self):
        return EventRelation.objects.filter(event__creator=self.request.user)


class MeetingDetailView(LoginRequiredMixin, DetailView):
    model = Meeting
    fields = '__all__'


class MeetingDeleteView(LoginRequiredMixin, DeleteView):
    '''
    Deleting schedule.Event removes relevant:
        schedule.EventRelation
        schedule.Occurrence
        schedule.Event
        
        ... so just need to delete schedule.Event and civic_calendar.Meeting
    '''
    success_url = reverse_lazy('meeting-list')
    template_name = 'civic_calendar/confirm_delete.html'
    model = EventRelation

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        meeting = Meeting.objects.get(pk=self.object.content_object.id)
        event = Event.objects.get(pk=self.object.event.id)
        if event.creator == request.user:
            meeting.delete()
            # Delete Event 2nd, as deletingn it deletes EventRelation as well
            # and meeting.delete() makes use of MeetingRelation.
            event.delete()
            self.object.delete()
            return HttpResponseRedirect(self.get_success_url())
        else:
            raise Http404('You are not the owner of this event.')

class OccurrenceListView(ListView):
    '''
    Display online meetings list/outputs InDesign-formatted text
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

    def render_to_response(self, context, **response_kwargs):
        request = self.request

        if request.META['HTTP_USER_AGENT'].count('Macintosh'):
            os = 'MAC'
        else:
            os = 'WIN'


        t = loader.get_template('civic_calendar/occurrence_list.html')
        c = RequestContext(request, {
            'event_relation_list': self.get_queryset(),
            'os': os,
            }
        )
        data = t.render(c)

        if os == 'WIN':
            data = data.replace(u'\n', u'\r\n') # Convert Unix line endings to Windows

        data = data.encode('utf-16-le')
        r = HttpResponse(data, content_type='text/plain')
        r['Content-Disposition'] = 'attachment; filename=cr.calendar.txt'
        return r
