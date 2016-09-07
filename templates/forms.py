from .models import Meeting, Entity
from schedule.models import Event, EventRelation, Calendar

from django import forms


class MeetingCreateViewForm(forms.ModelForm):
    entity = forms.ModelChoiceField(queryset=Entity.objects.order_by('name'))

    class Meta:
        model = Meeting
        fields = '__all__'

    # def save(self):
    #     meeting =
    #     event = Event(
    #         creator = self.request.user,
    #     )
