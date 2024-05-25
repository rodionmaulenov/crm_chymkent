from django.contrib import admin

from mothers.services.mother import on_primary_stage, on_first_visit_stage


class OnWhatStageFilter(admin.SimpleListFilter):
    """Display all instances on Primary and First Visit stage"""
    title = 'stages'
    parameter_name = "stage"

    def lookups(self, request, model_admin):
        return (
            ('primary_stage', 'primary stage'),
            ('first_visit_stage', 'first visit stage'),
        )

    def queryset(self, request, queryset):

        if self.value() == "primary_stage":
            return on_primary_stage(queryset)

        if self.value() == "first_visit_stage":
            return on_first_visit_stage(queryset)
