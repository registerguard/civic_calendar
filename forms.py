from django import forms

from .models import Meeting, Entity

class MeetingCreateViewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # passed by get_form_kwargs override in views.MeetingCreateView
        owner = kwargs.pop('owner')
        # now kwargs don't contain 'owner', so we can safely pass it to the
        # base class method
        super(MeetingCreateViewForm, self).__init__(*args, **kwargs)
        self.fields['entity'].queryset = Entity.objects.filter(owner=owner).order_by('name')

    # def __init__(self, *args, **kwargs):
    #     self.request = kwargs.pop('request', None)
    #     super(MeetingCreateViewForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Meeting
        fields = '__all__'

    # def save(self, creator, *args, **kwargs):
    #     f = super(MeetingCreateViewForm, self).save(creator, *args, **kwargs)
    #     return f
