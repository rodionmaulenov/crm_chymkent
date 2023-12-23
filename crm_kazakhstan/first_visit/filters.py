from django.contrib import admin

from mothers.models import Planned


class PlannedVisitListFilter(admin.SimpleListFilter):
    title = "planned tasks"
    parameter_name = "plan"

    def lookups(self, request, model_admin):
        """
        Show mothers instance on first visit with planned TAKE_TESTS and scheduled_date
        """
        qs = model_admin.get_queryset(request)

        if qs.filter(
                planned__plan=Planned.PlannedChoices.TAKE_TESTS,
                planned__scheduled_date__isnull=False
        ).exists():
            yield "tests", "Take tests"

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == "tests":
            return queryset.filter(
                planned__plan=Planned.PlannedChoices.TAKE_TESTS,
                planned__scheduled_date__isnull=False
            ).order_by('-planned__scheduled_date')

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


class AuthPlannedVisitListFilter(PlannedVisitListFilter):

    def lookups(self, request, model_admin):
        if request.user.is_superuser or self.can_view(request):
            return super().lookups(request, model_admin)

    def queryset(self, request, queryset):
        if request.user.is_superuser or self.can_view(request):
            return super().queryset(request, queryset)

    def can_view(self, request):
        return request.user.is_staff and request.user.has_perm('mothers.to_manager_on_first_stage')
