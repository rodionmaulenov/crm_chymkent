import pytz
from dateutil import parser

from django.utils.html import format_html
from django.db.models import Q
from django.contrib import admin
from django.db import models, IntegrityError, transaction
from django.utils.translation import ngettext
from django.contrib import messages
from django.utils import formats, timezone

from mothers.filters import AuthConditionListFilter
from mothers.inlines import ConditionInline, CommentInline, PlannedInline
from mothers.models import Mother, Comment, Condition, Stage, Planned
from mothers.services import get_difference_time, aware_datetime_from_date

Mother: models
Comment: models
Stage: models


@admin.register(Mother)
class MotherAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    ordering = ('-date_create',)
    inlines = [PlannedInline, ConditionInline, CommentInline, ]
    list_filter = ("date_create", AuthConditionListFilter)
    list_display = (
        'id', 'name', 'mother_date_created', 'number', 'residence', 'height_and_weight',
        'bad_habits', 'caesarean', 'children_age', 'age', 'citizenship', 'blood', 'maried',
    )

    actions = ('delete_selected', 'make_revoke', 'change_stage')

    list_display_links = ('name', 'residence',)
    readonly_fields = ('mother_date_created',)
    search_fields = ('number', 'program', 'residence__icontains',)
    view_on_site = False
    fieldsets = [
        (
            None,
            {
                "fields": [(
                    'name', 'number', 'program', 'residence', 'height_and_weight', 'mother_date_created',
                    'bad_habits', 'caesarean', 'children_age', 'age', 'citizenship', 'blood', 'maried'
                ), ],

                'description': 'This is the additional information section.',
            },
        ),
        (
            "Advanced options",
            {
                "classes": ['collapse'],
                "fields": [],
            },
        ),
    ]

    search_help_text = 'IN DATA QUERY USE PATTERNS LIKE  "D-M-Y"  "D-M"  "D"'

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Condition):
                utc_aware_time = get_difference_time(request, instance)
                instance.scheduled_time = utc_aware_time
                instance.save()
        formset.save_m2m()
        super().save_formset(request, form, formset, change)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        try:
            if search_term[:4].isdigit():
                search_date = parser.parse(search_term).date()
                aware_datetime = aware_datetime_from_date(search_date)
            else:
                search_date = parser.parse(search_term, dayfirst=True).date()
                aware_datetime = aware_datetime_from_date(search_date)

            queryset |= self.model.objects.filter(date_create__gte=aware_datetime)
        except parser.ParserError:
            pass

        return queryset, use_distinct

    def get_queryset(self, request):
        self.request = request
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'comment', 'condition', 'messanger', 'stage'
        ).exclude(Q(comment__revoked=True) | Q(stage__isnull=False))
        return queryset

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'make_revoke' in actions and not request.user.has_perm('mothers.revoke_mothers'):
            del actions['make_revoke']
        return actions

    @admin.action(description="Revoke mothers")
    def make_revoke(self, request, queryset):
        """
        Mother that already have Comment update this instance else
        create new related Comment instance
        """
        mother = queryset.count()
        Comment.objects.filter(mother__in=queryset).update(revoked=True)

        for mother in queryset.exclude(comment__isnull=False):
            Comment.objects.create(mother=mother, revoked=True)

        self.message_user(
            request,
            ngettext(
                f"{mother} mother was successfully revoked.",
                f"{mother} mothers were successfully revoked.",
                mother
            ),
            messages.SUCCESS,
        )

    @admin.action(description="First visit")
    def change_stage(self, request, queryset):
        """
        Now instance have Stage__stage from None become Primary
        If instance already have Stage__stage raise error IntegrityError
        """
        with transaction.atomic():
            mother_have_plan = queryset.filter(planned__plan__isnull=False,
                                               planned__plan=Planned.PlannedChoices.TAKE_TESTS)
            mother_without_plan = queryset.filter(planned__plan__isnull=True)

            new_stages = [Stage(mother=mother, stage=Stage.StageChoices.PRIMARY) for mother in mother_have_plan]
            try:
                Stage.objects.bulk_create(new_stages)
            except IntegrityError:
                self.message_user(request, format_html('Something wrong. Try again'), messages.ERROR)
                return

        messages_to_user = [
            (f"<strong>{mother}</strong> passed into the first visit page.", messages.SUCCESS)
            for mother in mother_have_plan
        ]

        messages_to_user.extend(
            (f"<strong>{mother}</strong> has not planned event.", messages.WARNING)
            for mother in mother_without_plan
        )
        for message, level in messages_to_user:
            self.message_user(request, format_html(message), level)

    @admin.display(empty_value="no date", description='date created')
    def mother_date_created(self, obj):
        user_timezone = getattr(self.request, 'timezone', 'UTC')

        user_tz = pytz.timezone(user_timezone)
        local_time = timezone.localtime(obj.date_create, timezone=user_tz)
        formatted_date = formats.date_format(local_time, "j M H:i")
        return formatted_date

    admin.site.disable_action('delete_selected')

    # @admin.display(empty_value="unknown", description='Documents')
    # def formatted_document_list(self, mother: Mother) -> str:
    #     """
    #     From instance verifies if all related documents exist return check mark
    #     otherwise return list documents that are not exist
    #
    #     :param mother: Mother model.Models
    #     :return: html string
    #     """
    #     actual_document_names = {
    #         'метрика ребенка', 'метрика мамы', 'нет судимости', 'нарколог', 'психиатр',
    #         'не в браке', 'загранпаспорт'
    #     }
    #     document_names = Mother.objects.filter(pk=mother.pk).values_list('document__name', flat=True)
    #
    #     if len(document_names) == 7:
    #         custom_icon_html = '<img src="/static/admin/img/icon-yes.svg" alt="True" style="width: 20px; height: 20px;" />'
    #         return format_html(custom_icon_html)
    #     else:
    #         html_string = '<div><select>'
    #
    #         for document_name in actual_document_names:
    #             if not (document_name in document_names):
    #                 html_string += f'<option>{document_name}</option>'
    #
    #         html_string += '</select></div>'
    #
    #         return format_html(html_string)

    # @admin.action(description="First visit")
    # def change_stage(self, request, queryset):
    #     for mother in queryset:
    #         try:
    #             if mother.planned.plan and mother.planned.plan in mother.planned.PlannedChoices.values:
    #                 obj, _ = Stage.objects.get_or_create(mother=mother, stage=Stage.StageChoices.PRIMARY)
    #                 self.message_user(
    #                     request,
    #                     format_html(f"<strong>{mother}</strong>  passed into first visit page."),
    #                     messages.SUCCESS,
    #                 )
    #         except Mother.planned.RelatedObjectDoesNotExist:
    #             self.message_user(
    #                 request,
    #                 format_html(f"<strong>{mother}</strong> has not planned event."),
    #                 messages.WARNING,
    #             )

    # @admin.action(description="First visit")
    # def change_stage(self, request, queryset):
    #     # Prefetch related planned objects to reduce database queries
    #     queryset = queryset.select_related('planned')
    #
    #     # Bulk updates can be used if applicable in your logic
    #     # stages_to_create = []
    #     messages_to_user = []
    #
    #     with transaction.atomic():  # Ensures database integrity
    #         for mother in queryset:
    #             if mother.planned.plan and mother.planned.plan in mother.planned.PlannedChoices.values:
    #                 Stage.objects.get_or_create(mother=mother, stage=Stage.StageChoices.PRIMARY)
    #                 messages_to_user.append(
    #                     (f"<strong>{mother}</strong> passed into first visit page.", messages.SUCCESS))
    #             else:
    #                 messages_to_user.append((f"<strong>{mother}</strong> has not planned event.", messages.WARNING))
    #
    #     # Send messages outside the loop
    #     for message, level in messages_to_user:
    #         self.message_user(request, format_html(message), level)

