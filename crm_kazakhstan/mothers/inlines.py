import pytz

from django.contrib import admin
from django.forms import BaseInlineFormSet
from datetime import datetime
from django.utils import timezone

from mothers.models import Condition, Comment


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
