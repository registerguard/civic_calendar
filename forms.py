from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Meeting, Entity, Location

class CalendarDateTimeWidget(forms.DateTimeInput):
    class Media:
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.15.0/moment.min.js',
            'js/bootstrap-datetimepicker.min.js',
        )


class MeetingCreateViewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # passed by get_form_kwargs override in views.MeetingCreateView
        owner = kwargs.pop('owner')
        # now kwargs don't contain 'owner', so we can safely pass it to the
        # base class method
        super(MeetingCreateViewForm, self).__init__(*args, **kwargs)
        self.fields['entity'].queryset = Entity.objects.filter(owner=owner).order_by('name')
        self.fields['location'].queryset = Location.objects.order_by('name')

    class Meta:
        model = Meeting
        fields = '__all__'
        widgets = {
            'start': CalendarDateTimeWidget(),
            'agenda': forms.Textarea(
                attrs={
                    'maxlength': '350',
                }
            ),
        }
        help_texts = {
            'start': _('<div class="alert alert-info"><b>Note:</b> Use military time.</div>'),
            'agenda': _('<div class="alert alert-info"><b>Note:</b> 350-character limit for Agenda description.</div>'),
        }
