from django import forms

from .models import Meeting

class MeetingCreateViewForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     self.request = kwargs.pop('request', None)
    #     super(MeetingCreateViewForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Meeting
        fields = '__all__'

    # def save(self, creator, *args, **kwargs):
    #     f = super(MeetingCreateViewForm, self).save(creator, *args, **kwargs)
    #     return f
