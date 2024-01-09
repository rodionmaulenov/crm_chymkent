from django.contrib import admin
from django.utils import timezone
from django.db.models import Q

from mothers.models import Planned


class ConditionListFilter(admin.SimpleListFilter):
    title = 'scheduler'
    parameter_name = "date_or_time"

    def __init__(self, *args, **kwargs):
        self.current_date = timezone.now().date()
        self.current_time = timezone.now().time()
        self.filtered_queryset_for_datetime = (
            # by_date_and_time: when scheduled_date == current_date then compare scheduled_time <= current_time
            Q(condition__scheduled_date=self.current_date,
                condition__scheduled_time__lte=self.current_time) |  # OR
            # by_date_and_time: if condition above wrong compare scheduled_date < current_date
            Q(condition__scheduled_date__lt=self.current_date)
            ) & Q(condition__finished=False)
        self.filtered_queryset_for_date = (
            # by_date: when scheduled_date <= current_date and scheduled_time is Empty
            Q(condition__scheduled_date__lte=self.current_date,
                condition__scheduled_time__isnull=True)
            ) & Q(condition__finished=False)
        super().__init__(*args, **kwargs)

    def lookups(self, request, model_admin):
        """
        Generates lookup choices for filtering. It offers two filtering options:
        - 'by_date': For conditions where the scheduled date is today or earlier, and the condition is not finished.
        - 'by_date_and_time': For conditions where the scheduled date is today and the scheduled time is earlier
        than now, or the scheduled date is past and the condition is not finished.

        Returns an iterator of tuples containing the internal query name and display title for each filter option.
        """
        qs = model_admin.get_queryset(request)

        if qs.filter(self.filtered_queryset_for_date).exists():
            yield "by_date", "entries by Date"

        if qs.filter(self.filtered_queryset_for_datetime).exists():
            yield "by_date_and_time", "entries by Time"

    def queryset(self, request, queryset):
        """
        Filters the queryset based on the selected filter option.
        It uses the value provided in the query string, retrievable via `self.value()`, to apply the appropriate filter.
        If 'by_date' is selected, it filters the queryset based on the date criteria.
        If 'by_date_and_time' is selected, it applies the date and time criteria.

        Returns the filtered queryset.
        """
        if self.value() == "by_date":
            return queryset.filter(self.filtered_queryset_for_date)
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
        if request.user.is_superuser or self.staff_user_with_perm(request):
            return super().lookups(request, model_admin)

    def queryset(self, request, queryset):
        if request.user.is_superuser or self.staff_user_with_perm(request):
            return super().queryset(request, queryset)

    def staff_user_with_perm(self, request):
        return request.user.is_staff and request.user.has_perm('mothers.change_mother')


class ReturnedFromFirstVisitListFilter(admin.SimpleListFilter):
    title = 'first visit'
    parameter_name = "returned"

    def lookups(self, request, model_admin):
        """
        Returned from first visit stage
        """

        qs = model_admin.get_queryset(request)

        if qs.filter(
                planned__plan=Planned.PlannedChoices.TAKE_TESTS,
                planned__note__isnull=False,
                planned__scheduled_date__isnull=False,
                stage__finished=True
        ).exists():
            yield "mothers", "returned from first visit"

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == "mothers":
            return queryset.filter(
                planned__plan=Planned.PlannedChoices.TAKE_TESTS,
                planned__note__isnull=False,
                planned__scheduled_date__isnull=False,
                stage__finished=True
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


class AuthReturnedFromFirstVisitListFilter(ReturnedFromFirstVisitListFilter):

    def lookups(self, request, model_admin):
        if request.user.is_superuser or self.can_view(request):
            return super().lookups(request, model_admin)

    def queryset(self, request, queryset):
        if request.user.is_superuser or self.can_view(request):
            return super().queryset(request, queryset)

    def can_view(self, request):
        return request.user.is_staff and request.user.has_perm('mothers.to_manager_on_primary_stage')
