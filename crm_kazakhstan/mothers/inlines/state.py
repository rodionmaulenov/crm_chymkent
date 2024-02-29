from datetime import date, time
from typing import Union

from django.contrib import admin
from django.db import models

from mothers.services.state import render_icon, format_date_or_time, has_permission
from mothers.models import State

Mother: models


class StateInline(admin.TabularInline):
    model = State
    extra = 0
    readonly_fields = ['display_state', 'display_reason', 'display_date', 'display_time', 'display_complete']
    fields = ['display_state', 'display_reason', 'display_date', 'display_time', 'display_complete']

    def get_queryset(self, request):
        # Get the default queryset with related 'mother'
        queryset = super().get_queryset(request).select_related('mother')
        queryset = queryset.exclude(condition=State.ConditionChoices.CREATED)

        return queryset

    def has_view_permission(self, request, obj=None):
        from mothers.admin import StateAdmin
        state_admin = StateAdmin(State, admin.site)
        return has_permission(state_admin, request, obj, 'view')

    @admin.display(description='state')
    def display_state(self, obj: State) -> str:
        return obj.get_condition_display()

    @admin.display(description='reason')
    def display_reason(self, obj: State) -> str:
        return obj.reason if obj.reason else '_'

    @admin.display(description='date')
    def display_date(self, obj: State) -> Union[date, str]:
        from mothers.services.mother import convert_utc_to_local

        if obj.scheduled_date and obj.scheduled_time:
            user_date = convert_utc_to_local(self.request, obj.scheduled_date, obj.scheduled_time)
            local_date = format_date_or_time(user_date.date())
            return local_date
        return '_'

    @admin.display(description='time')
    def display_time(self, obj: State) -> Union[time, str]:
        from mothers.services.mother import convert_utc_to_local

        if obj.scheduled_date and obj.scheduled_time:
            user_datetime = convert_utc_to_local(self.request, obj.scheduled_date, obj.scheduled_time)
            local_time = format_date_or_time(user_datetime.time())
            return local_time
        return '-'

    @admin.display(description='complete')
    def display_complete(self, obj: State) -> str:
        tru_or_false = obj.finished
        return render_icon(tru_or_false)
