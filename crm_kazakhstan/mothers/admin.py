"""
MotherAdmin Description:

    The MotherAdmin class is a customized Django admin interface for managing Mother instances.
    It provides tailored inline editing capabilities, search functionalities, and action handlers to manage
    the lifecycle and status of Mother instances based on specific business logic.

Custom Behaviors and Overriding:

    Inline Formsets:
        Incorporates inline formsets (PlannedInline, ConditionInline, CommentInline) allowing related objects
        to be edited directly within the Mother instance's admin page.

    Custom Queryset Handling:
        Customizes the queryset to exclude Mother instances that are banned or have moved to the first stage,
        ensuring only relevant instances are displayed for action.

    Search Enhancements:
        Extends search capabilities to include date-based filtering,
        enabling search for Mother instances from a specified date to the current date.

    Local Time Conversion:
        Converts date_create from UTC to the user's local timezone for display,
        providing a more contextually relevant timestamp for users.

    Custom Actions:
        Defines custom admin actions (banned and first_visit_stage) to transition Mother instances to different stages
        based on their associated data.

    Formset Customization:
        Dynamically adjusts inline form fields displayed, based on the finished state of conditions
        and certain time-based conditions met by the by_date_or_by_datatime service function.

    Field Rendering:
        Utilizes EmptyOnlyFieldWrapper for certain fields within inline forms to display custom content
        when fields are empty or when the associated Condition instance is finished.

    User Feedback:
        Provides user feedback messages for actions performed on Mother instances, indicating the outcome of each action.

    Date Formatting:
        Offers a custom display for the date_create field that formats the date according to user's local timezone settings.

By customizing the default admin behavior, MotherAdmin serves a specific workflow, providing a tailored administrative
interface that caters to the nuanced requirements of managing Mother instances in the system.
"""

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
from mothers.models import Mother, Comment, Stage, Planned, Condition
from mothers.services import (get_difference_time, aware_datetime_from_date, get_specific_fields,
                              by_date_or_by_datatime, check_queryset_logic)

Comment: models
Stage: models


@admin.register(Mother)
class MotherAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    ordering = ('-date_create',)
    inlines = (PlannedInline, ConditionInline, CommentInline,)
    list_filter = ("date_create", AuthConditionListFilter, AuthReturnedFromFirstVisitListFilter)
    list_display = (
        'id', 'name', 'mother_date_created', 'number', 'residence', 'height_and_weight',
        'bad_habits', 'caesarean', 'children_age', 'age', 'citizenship', 'blood', 'maried',
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
        actions = super().get_actions(request)
        if 'banned' in actions and not request.user.has_perm('mothers.move_to_ban'):
            del actions['banned']
        if 'first_visit_stage' in actions and not request.user.has_perm('mothers.action_first_visit'):
            del actions['first_visit_stage']
        return actions

    @admin.action(description="Ban")
    def banned(self, request, queryset):
        """
        Moved to ban instances if their Comment description is not equal None
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
    def first_visit_stage(self, request, queryset):
        """
        Initially queryset mother instances not contain relation with Stage because get_queryset exclude their
        Stage__stage for mother becomes Primary if planned__plan=TAKE_TESTS already exists
        """
        mother_have_plan = queryset.filter(planned__plan__isnull=False,
                                           planned__plan=Planned.PlannedChoices.TAKE_TESTS)
        for mother in mother_have_plan:
            Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
            self.message_user(
                request,
                format_html(f"<strong>{mother}</strong>  passed into first visit page."),
                messages.SUCCESS
            )

        mother_without_plan = queryset.exclude(planned__plan__isnull=False,
                                               planned__plan=Planned.PlannedChoices.TAKE_TESTS)
        for mother in mother_without_plan:
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
