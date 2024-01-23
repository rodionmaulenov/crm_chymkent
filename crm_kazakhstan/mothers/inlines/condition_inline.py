from datetime import date, time
from typing import Union

from django.contrib import admin

from mothers.services.condition import render_icon, format_date_or_time
from mothers.models import Condition, Mother


class ConditionInline(admin.TabularInline):
    model = Condition
    extra = 0
    readonly_fields = ['display_state', 'display_reason', 'display_date', 'display_time', 'display_complete']
    fields = ['display_state', 'display_reason', 'display_date', 'display_time', 'display_complete']

    def has_view_permission(self, request, obj=None):
        self.request = request
        from mothers.admin import MotherAdmin
        return MotherAdmin(Mother, admin.site).has_view_permission(request, obj)

    @admin.display(description='state')
    def display_state(self, obj: Condition) -> str:
        return obj.get_condition_display()

    @admin.display(description='reason')
    def display_reason(self, obj: Condition) -> str:
        return obj.reason if obj.reason else '_'

    @admin.display(description='date')
    def display_date(self, obj: Condition) -> Union[date, str]:
        from mothers.services.mother import convert_utc_to_local

        if obj.scheduled_date and obj.scheduled_time:
            user_date = convert_utc_to_local(self.request, obj.scheduled_date, obj.scheduled_time)
            local_date = format_date_or_time(user_date.date())
            return local_date
        return '_'

    @admin.display(description='time')
    def display_time(self, obj: Condition) -> Union[time, str]:
        from mothers.services.mother import convert_utc_to_local

        if obj.scheduled_date and obj.scheduled_time:
            user_datetime = convert_utc_to_local(self.request, obj.scheduled_date, obj.scheduled_time)
            local_time = format_date_or_time(user_datetime.time())
            return local_time
        return '_'

    @admin.display(description='complete')
    def display_complete(self, obj: Condition) -> str:
        tru_or_false = obj.finished
        return render_icon(tru_or_false)
