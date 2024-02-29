from django.contrib import admin

from mothers.services.state import filters_datetime
from mothers.services.mother import get_already_created, without_plan, we_are_working, ban_query


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


class BoardFilter(BaseSimpleListFilter):
    """Condition board filter."""
    title = 'board'
    parameter_name = "filter_set"

    def __init__(self, *args, **kwargs):
        for_datetime = filters_datetime()
        self.filtered_queryset_for_datetime = for_datetime
        super().__init__(*args, **kwargs)

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)

        queryset = get_already_created(qs)
        if queryset:
            yield 'created_status', 'new instance'

        if qs.filter(self.filtered_queryset_for_datetime).exists():
            yield "scheduled_event", "scheduled event"

        queryset = without_plan(qs)
        if queryset:
            yield 'assign_new_state', 'assign new state'

        queryset = we_are_working(qs)
        if queryset:
            yield 'already_working', 'already working'

    def queryset(self, request, queryset):
        if self.value() == 'created_status':
            filtered_qs = get_already_created(queryset)
            return filtered_qs

        if self.value() == "scheduled_event":
            return queryset.filter(self.filtered_queryset_for_datetime)

        if self.value() == 'assign_new_state':
            queryset = without_plan(queryset)
            return queryset

        if self.value() == 'already_working':
            queryset = we_are_working(queryset)
            return queryset


class BanFilter(BaseSimpleListFilter):
    title = 'ban'
    parameter_name = "ban"

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        queryset = ban_query(qs)
        if queryset:
            yield 'ban_exist', 'ban'

    def queryset(self, request, queryset):
        if self.value() == 'ban_exist':
            queryset = ban_query(queryset)
            return queryset


