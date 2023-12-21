import pytz

from django.contrib import admin
from django.forms import BaseInlineFormSet
from datetime import datetime
from django.utils import timezone

from mothers.models import Condition, Comment, Planned


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
    fields = ('plan', 'note')
    extra = 0

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "plan" and request.user.has_perm('mothers.to_manager_on_primary_stage'):
            kwargs["choices"] = [(Planned.PlannedChoices.TAKE_TESTS.value, Planned.PlannedChoices.TAKE_TESTS.label)]
        return super().formfield_for_choice_field(db_field, request, **kwargs)
