# https://docs.djangoproject.com/en/1.10/topics/class-based-views/generic-editing/#s-models-and-request-user
# http://django.cowhite.com/blog/adding-and-editing-model-objects-using-django-class-based-views-and-forms/
import datetime
import operator
import pytz

from braces.views import LoginRequiredMixin

from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader, RequestContext
from django.views.generic import CreateView, UpdateView, DetailView, ListView, \
    DeleteView
from schedule.models import Calendar, Event, EventRelation
from schedule.periods import Period
from .forms import MeetingCreateViewForm
from .models import Meeting


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
            title=u'{0} meeting'.format(meeting.entity.name),
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
        pacific = pytz.timezone('US/Pacific')
        custom_date = self.request.GET.get('date', '')
        if custom_date:
            tomorrow_and_day_after = pacific.localize(
                datetime.datetime.strptime(custom_date, '%Y%m%d') \
                + datetime.timedelta(days=1)
            )
        else:
            tomorrow_and_day_after = pacific.localize(
                datetime.datetime.now().replace(hour=0, minute=0) \
                + datetime.timedelta(days=1)
            )
        my_events = Event.objects.all()
        upcoming = Period(
            my_events, tomorrow_and_day_after, tomorrow_and_day_after+datetime.timedelta(days=2)
        )

        occurrence_list = upcoming.get_occurrences()
        event_list = [occurrence.event for occurrence in occurrence_list]
        # figure out an order_by based on content_object.entity.jurisdiction.name
        # Can't
        # But! ...
        # ordered = sorted(queryset, key=operator. \
        #       attrgetter('content_object.entity.jurisdiction.name'))
        # http://stackoverflow.com/questions/2412770/good-ways-to-sort-a-queryset-django
        queryset = EventRelation.objects.prefetch_related('content_object__entity__jurisdiction'). \
            filter(event_id__in=event_list)
        ordered = sorted(queryset, key=operator \
            .attrgetter('content_object.entity.jurisdiction.name', 'event.start'))

        for event_item in ordered:
            # replace u'\r\n' with u' ' in Agenda text
            event_item.content_object.agenda = event_item.content_object \
                .agenda.replace(u'\r\n', u' ')

        return ordered

    def render_to_response(self, context, **response_kwargs):
        request = self.request
        meetings = self.get_queryset()

        if request.META['HTTP_USER_AGENT'].count('Macintosh'):
            client_os = 'MAC'
        else:
            client_os = 'WIN'

        if meetings:
            # Upcoming meetings found ... 
            t = loader.get_template('civic_calendar/occurrence_list.html')
            c = RequestContext(
                request, {
                    'event_relation_list': meetings,
                    'os': client_os,
                }
            )
            data = t.render(c)

            if client_os == 'WIN':
                data = data.replace(u'\n', u'\r\n') # Convert Unix line endings to Windows

            data = data.encode('utf-16-le')
            r = HttpResponse(data, content_type='text/plain')
            r['Content-Disposition'] = 'attachment; filename=cr.calendar.txt'
        else:
            # No upcoming meetings found, so a regular web response, not a file-attachment one
            t = loader.get_template('civic_calendar/occurrence_list_screen.html')
            c = RequestContext(
                request, {
                    'event_relation_list': ['<p>No upcoming meetings found. Try again another day.</p>',],
                    'os': client_os,
                }
            )

            data = t.render(c)
            r = HttpResponse(data, content_type='text/html')
            r['Content-Disposition'] = 'inline'

        return r


class WebMeetingListView(ListView):
    '''
    Provide a Web view listing for public consumption.
    '''
    template_name = 'civic_calendar/meeting_list.html'
    def get_queryset(self):
        pacific = pytz.timezone('US/Pacific')
        my_events = Event.objects.all()
        my_today = pacific.localize(
            datetime.datetime.now().replace(hour=0, minute=0) \
        )
        upcoming = Period(
            my_events, my_today, my_today+datetime.timedelta(days=30)
        )
        event_id_list = [occurrence.event_id for occurrence in upcoming.get_occurrences()]
        return EventRelation.objects.filter(event_id__in=event_id_list)
