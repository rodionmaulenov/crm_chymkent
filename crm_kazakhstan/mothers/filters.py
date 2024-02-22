from django.contrib import admin
from django.utils import timezone

from mothers.services.condition import filters_datetime
from mothers.services.mother import get_already_created, get_empty_state


class BaseSimpleListFilter(admin.SimpleListFilter):
    def choices(self, changelist):
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string(remove=[self.parameter_name]),
        }
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == str(lookup),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": title,
            }


class PlannedTimeFilter(BaseSimpleListFilter):
    """Planned events filter"""
    title = 'planned'
    parameter_name = "planned_time"

    def __init__(self, *args, **kwargs):
        for_datetime = filters_datetime()
        self.filtered_queryset_for_datetime = for_datetime
        super().__init__(*args, **kwargs)

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)

        if qs.filter(self.filtered_queryset_for_datetime).exists():
            yield "datetime", "scheduled event"

    def queryset(self, request, queryset):
        if self.value() == "datetime":
            return queryset.filter(self.filtered_queryset_for_datetime)


class CreatedStatusFilter(BaseSimpleListFilter):
    """Already created instances show on filtered queryset page"""
    title = 'recently created'
    parameter_name = 'recently_created'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        filtered_qs = get_already_created(qs)
        if filtered_qs:
            yield 'status_created', 'created'

    def queryset(self, request, queryset):
        if self.value() == 'status_created':
            filtered_qs = get_already_created(queryset)
            return filtered_qs


class EmptyConditionFilter(BaseSimpleListFilter):
    """Show results that have an empty condition and at the same time have a description of the reason"""
    title = '__empty__ state'
    parameter_name = 'empty_state'

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)
        queryset = get_empty_state(queryset)
        if queryset:
            yield 'empty_condition', 'described reason'

    def queryset(self, request, queryset):
        if self.value() == 'empty_condition':
            queryset = get_empty_state(queryset)
            return queryset


class DateFilter(BaseSimpleListFilter):
    title = 'range creation'
    parameter_name = 'date_filter'

    def __init__(self, *args, **kwargs):
        self.now = timezone.now()
        self.yesterday = self.now - timezone.timedelta(days=1)
        self.seven_days_ago = self.now - timezone.timedelta(days=7)
        self.fourteen_days_ago = self.now - timezone.timedelta(days=14)
        self.start_of_month = self.now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        super().__init__(*args, **kwargs)

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('past_7_days', 'Past 7 Days'),
            ('past_14_days', 'Past 14 Days'),
            ('current_month', 'Current Month'),
        )

    def queryset(self, request, queryset):

        if self.value() == 'today':
            return queryset.filter(date_create__date=self.now)
        elif self.value() == 'yesterday':
            return queryset.filter(date_create__date=self.yesterday)
        elif self.value() == 'past_7_days':
            return queryset.filter(date_create__date__gte=self.seven_days_ago)
        elif self.value() == 'past_14_days':
            return queryset.filter(date_create__date__gte=self.fourteen_days_ago)
        elif self.value() == 'current_month':
            return queryset.filter(date_create__date__gte=self.start_of_month)
        return queryset


class ConditionDateFilter(DateFilter):
    def queryset(self, request, queryset):

        if self.value() == 'today':
            return queryset.filter(condition__created__date=self.now)
        elif self.value() == 'yesterday':
            return queryset.filter(condition__created__date=self.yesterday)
        elif self.value() == 'past_7_days':
            return queryset.filter(condition__created__date__gte=self.seven_days_ago)
        elif self.value() == 'past_14_days':
            return queryset.filter(condition__created__date__gte=self.fourteen_days_ago)
        elif self.value() == 'current_month':
            return queryset.filter(condition__created__date__gte=self.start_of_month)
        return queryset
