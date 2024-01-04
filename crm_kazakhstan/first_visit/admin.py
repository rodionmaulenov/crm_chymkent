from django.contrib import admin, messages
from django.db import models
from django.utils.html import format_html

from first_visit.filters import AuthPlannedVisitListFilter
from first_visit.inlines import PrimaryVisitPlannedInline
from first_visit.models import FirstVisit
from mothers.models import Stage, Planned, Mother

Stage: models
Planned: models
Mother: models


@admin.register(FirstVisit)
class PrimaryVisitAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = (AuthPlannedVisitListFilter,)
    inlines = (PrimaryVisitPlannedInline,)
    readonly_fields = (
        'name', 'number', 'program', 'residence', 'height_and_weight',
        'bad_habits', 'caesarean', 'children_age', 'age', 'citizenship', 'blood', 'maried'
    )
    fieldsets = [
        (
            "Private data",
            {
                "classes": ['collapse'],
                'fields': [
                    ('name', 'number', 'program'),
                    ('residence', 'height_and_weight', 'bad_habits'),
                    ('caesarean', 'children_age', 'age'),
                    ('citizenship', 'blood', 'maried'),
                ],
            }),
    ]

    actions = ('on_primary_stage',)

    def get_queryset(self, request):
        """
        We are getting queryset on Primary stage excluding instances that sent to the Ban
        """
        qs = Mother.objects.all()
        qs = qs.filter(stage__stage=Stage.StageChoices.PRIMARY, stage__finished=False).exclude(comment__banned=True)
        return qs

    def get_list_display(self, request):
        """
        Dynamically return a different list_display based on the filter selection
        """
        # Call the parent method to get the default list_display
        list_display = super().get_list_display(request)

        # Check if your specific filter is being used
        if 'plan' in request.GET and request.GET['plan'] == 'tests':
            # Return a custom list_display
            return 'name', 'first_planned_visit', 'first_planned_visit_date'

        return list_display

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'on_primary_stage' in actions and not request.user.has_perm('mothers.action_on_primary_stage'):
            del actions['on_primary_stage']
        return actions

    @admin.action(description="On primary stage")
    def on_primary_stage(self, request, queryset):
        """
        Return selected instances on primary stage
        """
        mother_have_plan = queryset.filter(
            planned__plan=Planned.PlannedChoices.TAKE_TESTS,
            planned__note__isnull=False,
            planned__scheduled_date__isnull=False,
        )
        # do this when instance is not can touch anybody else
        for mother in mother_have_plan:
            stage = mother.stage_set.last()
            stage.finished = True
            stage.save()

            self.message_user(
                request,
                format_html(f"<strong>{mother}</strong> returned on primary page."),
                messages.SUCCESS
            )

        mother_without_plan = queryset.exclude(
            planned__plan=Planned.PlannedChoices.TAKE_TESTS,
            planned__note__isnull=False,
            planned__scheduled_date__isnull=False,
        )
        for mother in mother_without_plan:
            self.message_user(
                request,
                format_html(f"<strong>{mother}</strong> indicate reason"),
                messages.WARNING
            )

    @admin.display(empty_value="not planned visit", description='planned visit')
    def first_planned_visit(self, obj):
        return Planned.objects.filter(mother=obj).first()

    @admin.display(empty_value="no date set", description='appointment date')
    def first_planned_visit_date(self, obj):
        return Planned.objects.filter(mother=obj).first().scheduled_date
