from django.conf.urls import url
from django.contrib.auth.views import login, logout, password_change,\
    password_change_done
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
        regex=r'^(?P<pk>\d+)/delete/$',
        view=views.MeetingDeleteView.as_view(),
        name='delete',
    ),
    url(
        regex=r'^(?P<pk>\d+)/$',
        view=views.MeetingDetailView.as_view(),
        name='meeting-detail',
    ),
    url(
        regex=r'^meetings/$',
        view=views.WebMeetingListView.as_view(),
        name='public-meeting-list',
    ),
    url(r'^accounts/login/$', login, name='login'),
    url(r'^accounts/logout/$', logout, {'next_page': '/civic/'}, name='logout'),
    url(
        r'^password_change/$',
        password_change,
        {'template_name': 'registration/password_change.html'},
        name='password_change',
    ),
    url(
        r'^password_change/done/$',
        password_change_done,
        {'template_name': 'registration/password_changed.html'},
        name='password_change_done',
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
