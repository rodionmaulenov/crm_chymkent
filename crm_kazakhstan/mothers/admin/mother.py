import pytz

from dateutil import parser

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.db.models import Count, Case, When, QuerySet
from django.contrib import admin, messages
from django.db import models
from django.utils import formats, timezone
from django.urls import reverse

from mothers.filters import AuthConditionListFilter, AuthReturnedFromFirstVisitListFilter
from mothers.inlines import ConditionInline, CommentInline, PlannedInline
from mothers.models import Mother, Comment, Stage, Condition
from mothers.services.mother import (get_difference_time, aware_datetime_from_date, get_specific_fields,
                                     by_date_or_by_datatime, check_queryset_logic,
                                     first_visit_action_logic_for_queryset,
                                     check_existence_of_latest_unfinished_plan, shortcut_bold_text,
                                     comment_plann_and_comment_finished_true, last_condition_finished_false,
                                     last_condition_finished_and_scheduled_date_false, last_condition_finished_true,
                                     meets_condition_list_filter_criteria, get_filter_value_from_url)

Comment: models
Stage: models
Mother: models
Planned: models


@admin.register(Mother)
class MotherAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    ordering = ('-date_create',)
    inlines = (PlannedInline, ConditionInline, CommentInline,)
    list_filter = ("date_create", AuthConditionListFilter, AuthReturnedFromFirstVisitListFilter)
    list_display = (
        'id', 'name', 'mother_date_created', 'number', 'residence', 'height_and_weight',
        'bad_habits', 'caesarean', 'children_age', 'age', 'citizenship', 'blood', 'maried',
        "create_condition_link",
    )

    actions = ('first_visit_stage', 'delete_selected', 'banned')

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

                'description': 'Client personal data',
            },
        )
    ]

    search_help_text = 'Search description'

    def response_post_save_change(self, request, obj):
        """
        Redirect to the changelist url if condition is equal 0 and mother instance get from filtered list.
        """
        condition = obj.condition_set.aggregate(
            unfinished_count=Count(Case(When(finished=False, then=1)))
        )

        time = by_date_or_by_datatime(request)

        if condition['unfinished_count'] == 0 and time:
            changelist_url = reverse('admin:mothers_mother_changelist')
            return HttpResponseRedirect(changelist_url)
        else:
            return super().response_post_save_change(request, obj)

    def get_formsets_with_inlines(self, request, obj=None):
        """
        Replace inline form to another for specific conditions
        """
        for inline in self.get_inline_instances(request, obj):
            inline = get_specific_fields(request, inline)
            yield inline.get_formset(request, obj), inline

    def save_formset(self, request, form, formset, change):
        """
        Pre-filling the “scheduled_time” form field with data
        that converts the time stored on the server into the user’s equivalent local time.
        """
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Condition) and instance.scheduled_time is not None:
                utc_aware_time = get_difference_time(request, instance)
                instance.scheduled_time = utc_aware_time
                instance.save()
        formset.save_m2m()

        super().save_formset(request, form, formset, change)

    def get_search_results(self, request, queryset, search_term):
        """
        User has possibility search instances from includes date input to date.today()
        """
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
        """
        Queryset contains exclusively the Mother instance where Stage.finished=True
        and not Comment.banned=True if exists
        """
        # assign request for using in custom MotherAdmin methods
        self.request = request
        qs = super().get_queryset(request)
        qs = check_queryset_logic(qs)
        return qs

    def get_actions(self, request):
        """
        It first retrieves the standard set of actions.
        Then, it checks the user's permissions for specific actions (like banning or performing first visit actions).
        Additionally, it verifies database conditions such as the existence of Mothers with comments and the presence
        of unfinished plans. Based on these checks, it dynamically removes certain actions from the available set
        if the user lacks permissions or if the relevant conditions in the database are not met.
        This ensures that the admin interface presents only the relevant and permitted actions to the user.
        """
        actions = super().get_actions(request)
        # Check user permissions
        has_ban_permission = request.user.has_perm('mothers.move_to_ban')
        has_first_visit_permission = request.user.has_perm('mothers.action_first_visit')

        # Check database conditions
        if Mother.objects.exists():
            has_comments = Mother.objects.filter(comment__description__isnull=False).exists()
            has_unfinished_plan = check_existence_of_latest_unfinished_plan()
            if not has_comments:
                del actions['banned']
            if not has_unfinished_plan:
                del actions['first_visit_stage']

        if 'banned' in actions and not has_ban_permission:
            del actions['banned']

        if 'first_visit_stage' in actions and not has_first_visit_permission:
            del actions['first_visit_stage']

        return actions

    @admin.action(description="Ban")
    def banned(self, request: WSGIRequest, queryset: QuerySet) -> None:
        """
        Comment.banned`s assign True when Comment.description not None and then move to Ban list
        """
        queryset_to_ban = queryset.filter(comment__description__isnull=False)
        Comment.objects.filter(mother__in=queryset_to_ban).update(banned=True)

        for mother in queryset_to_ban:
            self.message_user(
                request,
                format_html(f"<strong>{mother}</strong> has moved to ban"),
                messages.SUCCESS
            )

        queryset_not_to_ban = queryset.exclude(comment__description__isnull=False)
        for mother in queryset_not_to_ban:
            self.message_user(
                request,
                format_html(f"<strong>{mother}</strong> has no reason moved to ban"),
                messages.WARNING
            )

    @admin.action(description="First visit")
    def first_visit_stage(self, request: WSGIRequest, queryset: QuerySet) -> None:
        """
        The queryset already contains Stage instances with finished True

        Admin action to categorize and update selected 'Mother' instances based on their planning status.

        This function divides the mothers into two groups:
        - Those with an unfinished plan for a specific event (TAKE_TESTS).
        - Those without such a plan.

        Actions taken:
        - For the first group, a 'PRIMARY' stage instance is created and a success message is displayed.
        - For the second group, a warning message is shown about the lack of a planned event.

        This facilitates efficient tracking and management of mothers' progress.
        """
        mothers_with_plan, mothers_without_plan = first_visit_action_logic_for_queryset(queryset)

        for mother in mothers_with_plan:
            Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
            self.message_user(
                request,
                format_html(f"<strong>{mother}</strong> passed into first visit page."),
                messages.SUCCESS
            )

        for mother in mothers_without_plan:
            self.message_user(
                request,
                format_html(f"<strong>{mother}</strong> has not planned event."),
                messages.WARNING
            )

    @admin.display(empty_value="no date", description='date created')
    def mother_date_created(self, obj):
        """
        Returns time converted from UTC to user local timezone time
        """
        # receive this request from get_queryset method
        user_timezone = getattr(self.request.user, 'timezone', 'UTC')

        user_tz = pytz.timezone(str(user_timezone))
        local_time = timezone.localtime(obj.date_create, timezone=user_tz)

        formatted_date = formats.date_format(local_time, "j M H:i")
        return formatted_date

    @admin.display(description='Status/Time')
    def create_condition_link(self, obj: Mother) -> format_html:
        """
        Creates a display for a Mother object in the Django admin with condition-based links or statuses.

        The display logic is as follows:
        - If there's a comment or unfinished planned event, and the latest condition is finished,
        display the condition status.
        - If the latest condition is unfinished without a scheduled date, provide an edit link for this condition.
        - If the latest condition is unfinished with a scheduled date, display the status and the date,
        unless the admin view is filtered by condition criteria.
        - If the latest condition is finished, show the status with a link to add a new condition.
        - If the admin view is filtered by condition criteria, provide a link or status that reflects the filtered
        view's context.

        This method adapts the displayed link or status based on whether the admin view is showing all Mothers or
         a filtered subset based on condition criteria.

        :return: An HTML string containing the appropriate link or status.
        """
        condition_display = shortcut_bold_text(obj)

        comment, plan, condition = comment_plann_and_comment_finished_true(obj)

        filtered_condition = get_filter_value_from_url(self.request)

        if (comment or plan) and condition.finished:
            return format_html('{}', condition_display)

        if not condition.finished and not condition.scheduled_date:
            return last_condition_finished_and_scheduled_date_false(condition, self.request, condition_display)

        if not condition.finished and condition.scheduled_date and not filtered_condition:
            return last_condition_finished_false(condition, condition_display, self.request)

        if condition.finished:
            return last_condition_finished_true(obj, condition_display, self.request)

        if filtered_condition:
            return meets_condition_list_filter_criteria(condition, condition_display, self.request)

    admin.site.disable_action('delete_selected')
