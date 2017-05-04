from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit
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

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-8'
    helper.form_action = 'post'
    helper.form_action = 'create'

    helper.error_text_inline = True
    helper.help_text_inline = True

    helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Meeting
        fields = '__all__'
        widgets = {
            'start': CalendarDateTimeWidget(),
            'agenda': forms.Textarea(
                attrs={
                    'maxlength': '500',
                }
            ),
        }
        help_texts = {
            'start': _('<div class="alert alert-info"><b>Note:</b> Use military time.</div>'),
            'agenda': _('<div class="alert alert-info"><b>Note:</b> 500-character limit for Agenda description.</div>'),
        }
