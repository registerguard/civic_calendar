# ** http://stackoverflow.com/questions/27239783/how-to-use-django-scheduler-app-in-existing-app
# http://stackoverflow.com/questions/24327121/using-the-django-scheduler-app-with-your-own-models
# future
from __future__ import unicode_literals

# standard library
import datetime
import pytz

# third-party
from schedule.models import Event, EventRelation, Calendar

#Django
# from django.contrib.contenttypes.fields import GenericForeignKey
# from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _


@python_2_unicode_compatible
class Jurisdiction(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Entity(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, null=True)
    jurisdiction = models.ForeignKey(Jurisdiction)

    def __str__(self):
        return '({0}) {1}'.format(self.jurisdiction.name, self.name)

    class Meta:
        verbose_name_plural = 'entities'
        unique_together = (('name', 'owner', 'jurisdiction',),)


@python_2_unicode_compatible
class Location(models.Model):
    # geolocate on save:
    # http://stackoverflow.com/questions/2755027/geocoding-an-address-on-form-submission
    # ... or geopy?
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255, blank=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)

    def __str__(self):
        return u'({}) {}, {}'.format(self.city, self.name, self.address)

    class Meta:
        unique_together = (('name', 'address', 'city',),)

@python_2_unicode_compatible
class Meeting(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    start = models.DateTimeField(_("meeting start date and time"))
    location = models.ForeignKey(Location)
    agenda = models.TextField(blank=True)
    contact_phone = models.CharField(max_length=64, blank=True)
    contact_email = models.EmailField(blank=True)
    website = models.CharField(max_length=256, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    # Creates the "reverse" relationship
    # https://docs.djangoproject.com/en/1.9/ref/contrib/contenttypes/#s-reverse-generic-relations
    event_relation = GenericRelation(EventRelation)

    def __str__(self):
        # convert db UTC time to PT for presentation
        time_utc = self.start
        timezone_pt = pytz.timezone('America/Los_Angeles')
        time_local = time_utc.astimezone(timezone_pt)

        return u'({0}) {1}, {2} meeting'.format(self.entity.jurisdiction.name, self.entity.name, time_local.strftime('%A (%Y-%m-%d)'))

    def get_absolute_url(self):
        # page 109
        return reverse('meeting-detail', kwargs={'pk': self.pk})

    # def save(self, *args, **kwargs):
    #     new_meeting = False
    #     if not self.id:
    #         new_meeting = True
    #     super(Meeting, self).save(*args, **kwargs)
    #     end = self.start + datetime.timedelta(minutes=119)
    #     if new_meeting:
    #         event = Event(
    #             start=self.start,
    #             end=end,
    #             title='{0} meeting'.format(self.entity.name),
    #             description=self.agenda,
    #         )
    #         event.save()
    #         er = EventRelation.objects.create_relation(event, self)
    #         er.save()
    #         cal = Calendar.objects.get(name='civic')
    #         cal.events.add(event)
    #     else:
    #         event = Event.objects.get_for_object(self)[0]
    #         event.start = self.start
    #         event.end = end
    #         event.title = '{0} meeting'.format(self.entity.name)
    #         event.description = self.agenda
    #         event.save()
