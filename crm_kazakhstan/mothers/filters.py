from django.contrib import admin

from mothers.models import Mother
from mothers.services.condition import filter_condition_by_date_time


class ConditionListFilter(admin.SimpleListFilter):
    title = 'scheduler'
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


class AuthConditionListFilter(ConditionListFilter):
    def lookups(self, request, model_admin):
        if request.user.is_superuser or self.mother_admin_view_perm(request):
            return super().lookups(request, model_admin)

    def queryset(self, request, queryset):
        if request.user.is_superuser or self.mother_admin_view_perm(request):
            return super().queryset(request, queryset)

    def mother_admin_view_perm(self, request):
        from mothers.admin import MotherAdmin
        # obj parameter always empty
        return MotherAdmin(Mother, admin.site).has_view_permission(request, obj=None)
