from django import forms

from mothers.models import Condition
from mothers.services.mother import convert_utc_to_local


class ConditionAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.instance.pk and request:
            if self.instance.scheduled_date and self.instance.scheduled_time:
                local_datetime = convert_utc_to_local(request, self.instance.scheduled_date,
                                                      self.instance.scheduled_time)
                self.initial['scheduled_date'] = local_datetime.date()
                self.initial['scheduled_time'] = local_datetime.time()

    class Meta:
        model = Condition
        fields = '__all__'
