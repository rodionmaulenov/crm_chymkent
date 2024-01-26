from django.contrib import admin
from django.utils import timezone

from mothers.models import Mother
from mothers.services.condition import filter_condition_by_date_time


class MotherAdminViewPermMixin:
    def mother_admin_view_perm(self, request):
        from mothers.admin import MotherAdmin
        return MotherAdmin(Mother, admin.site).has_view_permission(request, obj=None)


class PermissionCheckingMixin(MotherAdminViewPermMixin):
    def has_permission(self, request):
        return request.user.is_superuser or self.mother_admin_view_perm(request)


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


class ConditionFilter(BaseSimpleListFilter):
    title = 'planned'
    parameter_name = "date_or_time"

    def __init__(self, *args, **kwargs):
        for_datetime = filter_condition_by_date_time()
        self.filtered_queryset_for_datetime = for_datetime
        super().__init__(*args, **kwargs)

    def lookups(self, request, model_admin):
        """
        Generates lookup choices for filtering. It offers two filtering options:
        - 'by_date_and_time': For conditions where the scheduled date is today and the scheduled time is earlier
        than now, or the scheduled date is past and the condition is not finished.

        Returns an iterator of tuples containing the internal query name and display title for each filter option.
        """
        qs = model_admin.get_queryset(request)

        if qs.filter(self.filtered_queryset_for_datetime).exists():
            yield "by_date_and_time", "entries by Time"

    def queryset(self, request, queryset):
        """
        Filters the queryset based on the selected filter option.
        It uses the value provided in the query string, retrievable via `self.value()`, to apply the appropriate filter.
        If 'by_date_and_time' is selected, it applies the date and time criteria.

        Returns the filtered queryset.
        """
        if self.value() == "by_date_and_time":
            return queryset.filter(self.filtered_queryset_for_datetime)


class AuthConditionFilter(ConditionFilter, PermissionCheckingMixin):
    def lookups(self, request, model_admin):
        if self.has_permission(request):
            return super().lookups(request, model_admin)

    def queryset(self, request, queryset):
        if self.has_permission(request):
            return super().queryset(request, queryset)


class DateFilter(BaseSimpleListFilter):
    title = 'date created'
    parameter_name = 'date_filter'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('past_7_days', 'Past 7 Days'),
            ('past_14_days', 'Past 14 Days'),
            ('current_month', 'Current Month'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()

        yesterday = now - timezone.timedelta(days=1)
        seven_days_ago = now - timezone.timedelta(days=7)
        fourteen_days_ago = now - timezone.timedelta(days=14)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if self.value() == 'today':
            return queryset.filter(date_create__date=now)
        elif self.value() == 'yesterday':
            return queryset.filter(date_create__date=yesterday)
        elif self.value() == 'past_7_days':
            return queryset.filter(date_create__date__gte=seven_days_ago)
        elif self.value() == 'past_14_days':
            return queryset.filter(date_create__date__gte=fourteen_days_ago)
        elif self.value() == 'current_month':
            return queryset.filter(date_create__date__gte=start_of_month)
        return queryset


class AuthDateFilter(DateFilter, PermissionCheckingMixin):
    def lookups(self, request, model_admin):
        if self.has_permission(request):
            return super().lookups(request, model_admin)

    def queryset(self, request, queryset):
        if self.has_permission(request):
            return super().queryset(request, queryset)
