import pytz

from django.contrib import admin
from django.forms import BaseInlineFormSet
from datetime import datetime
from django.utils import timezone
from django import forms

from mothers.models import Condition, Comment, Planned


class ConditionInlineForm(forms.ModelForm):
    class Meta:
        model = Condition
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        scheduled_time = cleaned_data.get("scheduled_time")
        scheduled_date = cleaned_data.get("scheduled_date")

        if scheduled_time and not scheduled_date:
            self.add_error('scheduled_date', "Date must be provided if time is set.")

        return cleaned_data


class CustomInlineFormset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        conversion_date = timezone.localdate()

        for form in self.forms:
            if form.instance.pk:
                scheduled_time = form.instance.scheduled_time
                if scheduled_time:
                    # Create a datetime object by combining the date and time
                    naive_datetime = datetime.combine(conversion_date, scheduled_time)

                    # Convert the naive datetime to an aware datetime in UTC
                    aware_datetime = timezone.make_aware(naive_datetime, timezone.utc)

                    # Convert the aware datetime to the user's timezone
                    user_timezone = getattr(self.request.user, 'timezone', 'UTC')
                    user_tz = pytz.timezone(str(user_timezone))
                    local_datetime = aware_datetime.astimezone(user_tz)

                    # Update the initial time of the form
                    form.initial['scheduled_time'] = local_datetime.time()


class ConditionInline(admin.TabularInline):
    model = Condition
    extra = 0
    formset = CustomInlineFormset
    form = ConditionInlineForm

    def get_formset(self, request, obj=None, **kwargs):
        FormsetClass = super().get_formset(request, obj, **kwargs)
        FormsetClass.request = request
        return FormsetClass


class CommentInline(admin.TabularInline):
    model = Comment
    fields = ('description',)
    extra = 0


class PlannedInline(admin.TabularInline):
    model = Planned
    fields = ('plan', 'note', 'scheduled_date')
    extra = 0

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "plan" and request.user.has_perm('mothers.to_manager_on_primary_stage'):
            kwargs["choices"] = [(Planned.PlannedChoices.TAKE_TESTS.value, Planned.PlannedChoices.TAKE_TESTS.label)]
        else:
            kwargs["choices"] = []
        return super().formfield_for_choice_field(db_field, request, **kwargs)
