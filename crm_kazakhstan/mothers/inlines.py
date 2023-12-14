from django import forms
from django.contrib import admin
from django.forms import BaseInlineFormSet
from django.utils import timezone

from mothers.models import Condition, Comment

from datetime import datetime, timedelta
import pytz


class ConditionForm(forms.ModelForm):
    class Meta:
        model = Condition
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user_timezone = kwargs.pop('user_timezone', 'UTC')
        super().__init__(*args, **kwargs)
        if self.instance.pk:  # check if instance is already created
            user_input_date = timezone.now()
            user_tz = pytz.timezone(str(user_timezone))
            local_datetime = user_input_date.astimezone(user_tz)
            self.initial['scheduled_date'] = local_datetime.date()
            self.initial['scheduled_time'] = local_datetime.time()
        self.fields['scheduled_date'].widget.format = '%Y-%m-%d'
        self.fields['scheduled_date'].widget.attrs['timezone'] = user_timezone
        self.fields['scheduled_time'].widget.format = '%H:%M:%S'
        self.fields['scheduled_time'].widget.attrs['timezone'] = user_timezone


class ConditionInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.user_timezone = kwargs.pop('user_timezone', 'UTC')
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs['user_timezone'] = self.user_timezone
        return super()._construct_form(i, **kwargs)


class ConditionInline(admin.TabularInline):
    model = Condition
    extra = 0
    form = ConditionForm
    formset = ConditionInlineFormSet

    def get_formset(self, request, obj=None, **kwargs):
        Formset = super().get_formset(request, obj, **kwargs)
        user_timezone = getattr(request.user, 'timezone', 'UTC')

        class WrappedFormset(Formset):
            def __init__(self, *args, **kwargs):
                kwargs['user_timezone'] = user_timezone
                super().__init__(*args, **kwargs)

        return WrappedFormset



class CommentInline(admin.TabularInline):
    model = Comment
    fields = ('description',)
    extra = 0
