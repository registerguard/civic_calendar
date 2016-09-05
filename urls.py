from django.conf.urls import url
from schedule.views import CalendarByPeriodsView

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.MeetingListView.as_view(),
        name='meeting-list',
    ),
    url(
        regex=r'^print/$',
        view=views.OccurrenceListView.as_view(),
        name='upcoming-occurrences',
    ),
    url(
        regex=r'^add/$',
        view=views.MeetingCreateView.as_view(),
        name='create',
    ),
    url(
        regex=r'^(?P<pk>\d+)/update/$',
        view=views.MeetingUpdateView.as_view(),
        name='update',
    ),
    url(
        regex=r'^(?P<pk>\d+)/$',
        view=views.MeetingDetailView.as_view(),
        name='meeting-detail',
    ),
    # url(
    #     regex=r'^(?P<calendar_slug>\w+)/$',
    #     view=CalendarByPeriodsView.as_view(),
    #     name='calendar-by-periods',
    # ),
]

# Figure this out:
# http://django-scheduler.readthedocs.io/en/latest/settings.html#get-events-func
#
# Working on getting
# http://internet02.guardnet.com:8000/civic/civic/?period=Day
# working ...
