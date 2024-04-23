from datetime import date, time
from typing import Union

from django.contrib import admin
from django.utils.html import format_html
from django.db import models

from mothers.models import State
from mothers.services.state import render_icon
from mothers.services.mother import convert_utc_to_local
from mothers.services.mother_classes.formatter_interface import DayMonthYearFormatter, HourMinuteFormatter

State: models


class StateInline(admin.TabularInline):
    model = State
    extra = 0
    readonly_fields = ['display_state', 'display_reason', 'display_date', 'display_time', 'display_icon']
    fields = ['display_state', 'display_reason', 'display_date', 'display_time', 'display_icon']

    def get_queryset(self, request):
        self.request = request
        # Get the default queryset with related 'mother'
        queryset = super().get_queryset(request).select_related('mother')
        queryset = queryset.exclude(condition=State.ConditionChoices.CREATED)

        return queryset

    def has_view_permission(self, request, state=None):
        return True

    @admin.display(description='state')
    def display_state(self, state: State) -> str:
        return format_html('<strong>{}</strong>', state.get_condition_display().upper())

    @admin.display(description='reason')
    def display_reason(self, state: State) -> str:
        return state.reason if state.reason else '-'

    @admin.display(description='scheduled date')
    def display_date(self, state: State) -> Union[date, str]:
        """
        Gets obj from database because on StateAdmin not exist fields:
        scheduled_date, scheduled_time
        """
        state_obj = State.objects.get(pk=state.pk)

        local_time = convert_utc_to_local(self.request, state_obj.scheduled_date, state_obj.scheduled_time)
        formatter = DayMonthYearFormatter()
        formatting = formatter.format(local_time)
        return formatting

    @admin.display(description='scheduled time')
    def display_time(self, state: State) -> Union[time, str]:
        """
        Gets obj from database because on StateAdmin not exist fields:
        scheduled_date, scheduled_time
        """
        state_obj = State.objects.get(pk=state.pk)

        local_time = convert_utc_to_local(self.request, state_obj.scheduled_date, state_obj.scheduled_time)
        formatter = HourMinuteFormatter()
        formatting = formatter.format(local_time)
        return formatting

    @admin.display(description='completed')
    def display_icon(self, state: State) -> str:
        tru_or_false = state.finished
        return render_icon(tru_or_false)
