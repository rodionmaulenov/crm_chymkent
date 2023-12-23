from django.contrib import admin

from first_visit.filters import AuthPlannedVisitListFilter
from first_visit.models import FirstVisit
from mothers.models import Stage
from django.contrib import messages
from django.utils.html import format_html
from django.db import models

Stage: models


@admin.register(FirstVisit)
class PrimaryVisitAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = (AuthPlannedVisitListFilter,)
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

    actions = ('change_stage',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'comment', 'condition', 'messanger', 'stage'
        ).filter(stage__stage=Stage.StageChoices.PRIMARY).exclude(comment__revoked=True)
        return queryset

    # @admin.action(description="Return on Primary state")
    # def change_stage(self, request, queryset):
    #     mother_have_plan = queryset.filter(planned__plan__isnull=False, planned__plan__in=Planned.PlannedChoices.values)
    #     mother_without_plan = queryset.filter(planned__plan__isnull=True)
    #
    #     new_stages = [Stage(mother=mother, stage=Stage.StageChoices.PRIMARY) for mother in mother_have_plan]
    #     Stage.objects.bulk_create(new_stages)
    #
    #     messages_to_user = [
    #         (f"<strong>{mother}</strong> passed into the first visit page.", messages.SUCCESS)
    #         for mother in mother_have_plan
    #     ]
    #
    #     messages_to_user.extend(
    #         (f"<strong>{mother}</strong> has not planned event.", messages.WARNING)
    #         for mother in mother_without_plan
    #     )
    #     for message, level in messages_to_user:
    #         self.message_user(request, format_html(message), level)

    class Media:
        css = {
            'all': ('first_visit/admin/css/align_fields.css',)
        }
