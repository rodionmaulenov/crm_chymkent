from django.contrib import admin
from django.utils.html import format_html
from django.db import models

from mothers.models import Planned
from mothers.services.mother import convert_utc_to_local
from mothers.services.mother_classes.formatter_interface import DayMonthYearFormatter, HourMinuteFormatter
from mothers.services.state import render_icon

Planned: models


class PlannedInline(admin.TabularInline):
    model = Planned
    extra = 0
    fields = ('display_plan', 'display_note', 'display_date', 'display_time', 'display_icon')
    readonly_fields = ('display_plan', 'display_note', 'display_date', 'display_time', 'display_icon')

    class Media:
        css = {
            'all': ('mothers/css/hide-inline-descriptions.css',)
        }

    def get_queryset(self, request):
        self.request = request

        queryset = super().get_queryset(request).select_related('mother')
        return queryset

    def has_view_permission(self, request, obj=None):
        return True

    @admin.display(description='plan')
    def display_plan(self, planned: Planned):
        return format_html('<strong>{}</strong>', planned.get_plan_display().upper())

    @admin.display(description='note')
    def display_note(self, planned: Planned):
        return planned.note if planned.note else '-'

    @admin.display(description='planned date')
    def display_date(self, planned: Planned):
        """
        Gets obj from database because on PlannedAdmin not exist fields:
        scheduled_date, scheduled_time
        """
        plan = Planned.objects.get(pk=planned.pk)

        local_time = convert_utc_to_local(self.request, plan.scheduled_date, plan.scheduled_time)
        formatter = DayMonthYearFormatter()
        formatting = formatter.format(local_time)
        return formatting

    @admin.display(description='planned time')
    def display_time(self, planned: Planned):
        """
        Gets obj from database because on PlannedAdmin not exist fields:
        scheduled_date, scheduled_time
        """
        plan = Planned.objects.get(pk=planned.pk)

        local_time = convert_utc_to_local(self.request, plan.scheduled_date, plan.scheduled_time)
        formatter = HourMinuteFormatter()
        formatting = formatter.format(local_time)
        return formatting

    @admin.display(description='completed')
    def display_icon(self, planned: Planned) -> str:
        tru_or_false = planned.finished
        return render_icon(tru_or_false)
