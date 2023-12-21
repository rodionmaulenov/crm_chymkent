from django.contrib import admin
from django.utils import timezone


class ConditionListFilter(admin.SimpleListFilter):
    title = 'scheduler'
    parameter_name = "date_or_time"

    def lookups(self, request, model_admin):
        """
        Only show search results that actually match
        the scheduled dates and times.
        """

        qs = model_admin.get_queryset(request)

        if qs.filter(
                condition__condition__isnull=False,
                condition__scheduled_date__lte=timezone.now().date(),
                condition__scheduled_time__isnull=True,
        ).exists():
            yield "by_date", "Entries by Date"

        if qs.filter(
                condition__condition__isnull=False,
                condition__scheduled_date__lte=timezone.now().date(),
                condition__scheduled_time__lte=timezone.now().time()
        ).exists():
            yield "by_date_and_time", "Entries by Time"

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == "by_date":
            return queryset.filter(
                condition__condition__isnull=False,
                condition__scheduled_date__lte=timezone.now().date(),
                condition__scheduled_time__isnull=True,
            )
        if self.value() == "by_date_and_time":
            return queryset.filter(
                condition__condition__isnull=False,
                condition__scheduled_date__lte=timezone.now().date(),
                condition__scheduled_time__lte=timezone.now().time()
            )

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
        if request.user.is_superuser or self.can_view(request):
            return super().lookups(request, model_admin)

    def queryset(self, request, queryset):
        if request.user.is_superuser or self.can_view(request):
            return super().queryset(request, queryset)

    def can_view(self, request):
        return request.user.is_staff and request.user.has_perm('mothers.to_manager_on_primary_stage')




