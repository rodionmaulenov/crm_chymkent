import pytz

from datetime import datetime, time, date
from typing import Tuple, Optional, Union

from django.contrib.admin import ModelAdmin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone, formats
from django.utils.http import urlencode
from django.db import models
from django.db.models import Subquery, OuterRef, QuerySet, CharField, Q
from django.utils.html import format_html, mark_safe
from django.utils.safestring import SafeString
from guardian.shortcuts import get_objects_for_user

from mothers.models import Stage, Planned, Comment, Condition, Mother
from mothers.services.condition import filter_condition_by_date_time, queryset_with_filter_condition

Stage: models
Planned: Stage
Comment: models
Condition: models


def convert_local_to_utc(request: HttpRequest, instance: Condition) -> datetime:
    """
    Converts the scheduled date and time of a Condition instance from the user's local timezone to UTC.
    """

    # Convert string to a timezone object
    user_timezone = pytz.timezone(str(request.user.timezone))

    # Combine date and time into a datetime object
    future_local_datetime = datetime.combine(instance.scheduled_date, instance.scheduled_time)

    # Make the datetime object timezone-aware in the user's local timezone
    future_local_aware = user_timezone.localize(future_local_datetime)

    # Convert the local timezone-aware datetime to UTC
    utc_datetime = future_local_aware.astimezone(pytz.utc)

    return utc_datetime


def convert_utc_to_local(request: HttpRequest, utc_date: date, utc_time: time) -> datetime:
    user_timezone = getattr(request.user, 'timezone', 'UTC')
    # Convert string to a timezone object
    user_timezone = pytz.timezone(str(user_timezone))

    # Combine UTC date and time strings into a datetime object
    utc_datetime_naive = datetime.combine(utc_date, utc_time)

    # Make the datetime object timezone-aware in UTC
    utc_datetime_aware = pytz.utc.localize(utc_datetime_naive)

    # Convert the UTC timezone-aware datetime to user's local timezone
    local_datetime = utc_datetime_aware.astimezone(user_timezone)

    return local_datetime


def on_primary_stage(queryset: QuerySet) -> QuerySet:
    """
    Get only mothers where Stage is Primary
    """
    # Subquery to get the latest stage for each mother
    latest_stage_subquery = Stage.objects.filter(
        mother=OuterRef('pk')
    ).order_by('-date_create').values('stage')[:1]

    # Annotate the queryset with the latest stage
    queryset = queryset.annotate(
        latest_stage=Subquery(latest_stage_subquery)
    )

    # Filter mothers whose latest stage is PRIMARY
    queryset = queryset.filter(latest_stage=Stage.StageChoices.PRIMARY)

    return queryset


def convert_to_local_time(obj: Mother, user_timezone: str) -> timezone.datetime:
    """
    Converts the 'date_create' of a Mother instance from UTC to the user's local timezone.
    """
    user_tz = pytz.timezone(str(user_timezone))
    return timezone.localtime(obj.date_create, timezone=user_tz)


def output_time_format(local_scheduled_datetime: Optional[datetime]) -> str:
    """
    Formats the provided datetime. Formats as 'Day Month Hour:Minute'.
    """
    return formats.date_format(local_scheduled_datetime, "j M H:i")


def comment_plann_and_comment_finished_true(obj: Mother) -> Tuple[Planned, Comment, Condition]:
    """
    Determines if there exists either a 'Planned' instance with specific criteria
    or a non-empty 'Comment' for a given 'Mother' object or 'Condition'.
    """
    planned = Planned.objects.filter(
        mother=obj,
        plan=Planned.PlannedChoices.TAKE_TESTS,
        finished=False
    )

    comment = Comment.objects.filter(
        mother=obj,
        description__isnull=False
    )

    condition = obj.condition_set.order_by('-id').first()

    return planned, comment, condition


def set_url_when_change_or_add_condition_object(request: HttpRequest) -> None:
    """
    Adding to request the earlier URL from where came when execute change 'Condition' object
    """
    request.session['previous_url'] = request.get_full_path()


def shortcut_bold_text(obj: Mother) -> format_html:
    """
    Retrieves the last condition for a `Mother` object, and returns
    its display string in a bold HTML format. The display string is truncated to 18 characters
    if it's longer than 17 characters.
    """
    # Using 'exists' to check if there is at least one finished condition
    if obj.condition_set.order_by('-id').exists():
        latest_condition = obj.condition_set.order_by('-id').first()

        if latest_condition.condition is None:
            for_display = latest_condition.reason
        else:
            for_display = latest_condition.get_condition_display()

        # Truncate and format the display text
        for_display = (for_display[:18] + '...') if len(for_display) > 16 else for_display
        return mark_safe(f'<strong>{for_display}</strong>')


def get_css_style(link_class: str, default_color: str, hover_color: str) -> str:
    """
    Generates a CSS style for a given link class with specified colors for default and hover states.
    """
    return f"""
        <style>
            a.{link_class} {{
                color: {default_color}; /* Default color */
            }}
            a.{link_class}:hover {{
                color: {hover_color}; /* Color on hover */
            }}
        </style>
    """


def create_link_html(url: str, link_class: str, display_text: str) -> format_html:
    """
    Creates string link with specified URL, CSS class, and display text.
    """
    return f'<a href="{url}" class="{link_class}">{display_text}</a>'


def get_filter_value_from_url(request: HttpRequest) -> bool:
    """
    Checks the request URL for specific 'date_or_time' filter parameters.
    """
    if 'date_or_time' in request.GET:
        filter_value = request.GET['date_or_time']
        return filter_value == 'by_date_and_time'


def condition_not_on_filtered_queryset(condition: Condition) -> bool:
    """
    Verify mother instance NOT on filtered change list Page return True otherwise False
    """
    current_date = timezone.now().date()
    current_time = timezone.now().time()
    return condition.scheduled_date > current_date or (
            condition.scheduled_date == current_date and condition.scheduled_time
            and condition.scheduled_time > current_time
    )


def add_new_condition(obj: Mother, condition_display: str, request: HttpRequest) -> format_html:
    """
    Generates an HTML link to add a new "Condition" in the Django admin interface for a specific Mother object.
    This is used when the last condition is marked as finished (True).
    """

    condition_add_url = reverse('admin:mothers_condition_add')
    current_path = request.get_full_path()
    return_path = urlencode({'_changelist_filters': current_path})

    return format_html(f'<a href="{condition_add_url}?mother={obj.pk}&{return_path}">{condition_display}</a>')


def change_condition_on_change_list_page(condition: Condition, request: HttpRequest,
                                         condition_display: str) -> format_html:
    """
    Change Url on mother change list Page to the specific 'Condition' instance
    where finished and scheduled_date are None.
    """
    change_url = reverse('admin:mothers_condition_change', args=[condition.pk])
    current_path = request.get_full_path()
    return_path = urlencode({'_changelist_filters': current_path})

    css_style = get_css_style("light-green", "green", "rgba(0, 150, 0, 0.8)")
    link_html = create_link_html(f'{change_url}?mother={condition.pk}&{return_path}', "light-green", condition_display)

    set_url_when_change_or_add_condition_object(request)

    return mark_safe(f'{css_style}{link_html}')


def change_or_not_based_on_filtered_queryset(condition: Condition, condition_display: str, request: HttpRequest) -> \
        Optional[format_html]:
    """
    CHANGE URL if mother instance on change list Page or SIMPLE STRING iN BOLD if mother instance
    on filtered change list Page.
    """
    local_datetime = convert_utc_to_local(request, condition.scheduled_date, condition.scheduled_time)
    formatted_datetime = output_time_format(local_datetime)

    change_url = reverse('admin:mothers_condition_change', args=[condition.pk])

    css_style = get_css_style("light-green", "green", "rgba(0, 150, 0, 0.8)")
    display_text = mark_safe(f'{condition_display}')
    link_html = create_link_html(change_url, "light-green", display_text)
    link_with_style = f'{css_style}{link_html}'

    if condition_not_on_filtered_queryset(condition):

        set_url_when_change_or_add_condition_object(request)

        return mark_safe(f'{link_with_style}/<br>{formatted_datetime}')
    else:
        return mark_safe(f'{condition_display}/<br>{formatted_datetime}')


def change_on_filtered_changelist(condition: Condition, condition_display: str, request: HttpRequest) -> format_html:
    """
    Can Change 'Condition instance' on filtered change list page.
    """
    local_datetime = convert_utc_to_local(request, condition.scheduled_date, condition.scheduled_time)
    formatted_datetime = output_time_format(local_datetime)

    change_url = reverse('admin:mothers_condition_change', args=[condition.pk])

    css_style = get_css_style("violet-link", "rgba(138, 43, 226, 0.8)", "violet")
    # Create link only for condition_display
    link_html = create_link_html(change_url, "violet-link", condition_display)

    # Combine the link with the formatted date, keeping the date outside of the hyperlink
    combined_html = f'{css_style}{link_html}/<br>{formatted_datetime}'

    # designate full url path for this change
    set_url_when_change_or_add_condition_object(request)

    return mark_safe(combined_html)


def get_model_objects(adm: ModelAdmin, request: HttpRequest) -> QuerySet:
    """
    Retrieves a QuerySet of objects from the model associated with the provided MotherAdmin instance (`adm`).
    The objects are filtered based on the user's permissions. It checks if the user has either 'view' or 'change'
    permissions for the objects of the model.

    This function is useful in scenarios where you want to display or provide access to objects that a specific user
    is allowed to view or change, according to their permissions.

    :param adm: The ModelAdmin instance related to the model whose objects are to be retrieved.
    :param request: The current HTTP request, containing the user for whom to check permissions.
    :return: A QuerySet of objects that the user has permission to view or change.
    """
    _meta = adm.opts
    actions = ['view', 'change']  # Define the permissions to check
    perms = [f'{perm}_{_meta.model_name}' for perm in actions]  # Construct permission codenames
    klass = _meta.model  # The model class associated with the ModelAdmin

    # Retrieve and return the objects for which the user has the specified permissions
    return get_objects_for_user(user=request.user, perms=perms, klass=klass, any_perm=True)


def has_permission(adm: ModelAdmin, request: HttpRequest, obj: Mother, action: str, base_permission: bool) -> bool:
    """
    Checks if the user has the specified permission for the given object. If the user has model lvl permission,
    or if the user has the specific permission on the object, it returns True. If the object is not specified,
    it checks if there are any objects in the primary stage for the user or if the base permission is True.
    """
    _meta = adm.opts
    code_name = f'{action}_{_meta.model_name}'
    if obj:
        return request.user.has_perm(f'{_meta.app_label}.{code_name}', obj) \
            or request.user.has_perm(f'{_meta.app_label}.{code_name}')  # in this case add user only view perm

    data = on_primary_stage(get_model_objects(adm, request))
    return data.exists() or base_permission


# Break down the large function into smaller functions
def handle_comment_or_plan_exists(condition, condition_display):
    """Handle cases where 'Comment' or 'Plan' instances exist."""
    if condition.finished:
        return format_html('{}', condition_display)


def handle_not_finished_condition(condition, condition_display, filtered_queryset_url, request):
    """Handle cases where the condition is not finished."""
    # if not condition.scheduled_date:
    #     return change_condition_on_change_list_page(condition, request, condition_display)

    if condition.scheduled_date and not filtered_queryset_url:
        return change_or_not_based_on_filtered_queryset(condition, condition_display, request)


def determine_link_action(request: HttpRequest, obj: Mother) -> Union[str, SafeString]:
    """
    Create a link based on the condition of the 'Mother' object.

    The function handles different cases:
    1. If a 'Comment' or 'Planned' instance exists related to Mother object, and 'Condition' is finished, no change is allowed.
    2. If only the state of condition instance exists (not finished, no scheduled date), the condition can be changed.
    3. Handles cases based on the presence of a scheduled date and whether the condition appears in a filtered queryset.
    4. If the last related 'Condition' instance is finished, a new 'Condition' can be added.
    5. Handles the case where the mother instance is located in a filtered queryset, allowing condition change.
    """
    condition_display = shortcut_bold_text(obj)
    comment, plan, condition = comment_plann_and_comment_finished_true(obj)
    filter_in_url = get_filter_value_from_url(request)

    if comment or plan:
        return handle_comment_or_plan_exists(condition, condition_display)

    if condition.finished and not (comment or plan):
        return add_new_condition(obj, condition_display, request)

    if not condition.finished and not filter_in_url:
        return handle_not_finished_condition(condition, condition_display, filter_in_url, request)

    if not condition.finished and filter_in_url:
        return change_on_filtered_changelist(condition, condition_display, request)

    return format_html('Condition status not determined.')


def get_for_datetime_queryset() -> bool:
    """
    Get the queryset(True or False) for the 'date_or_time' lookup.
    """
    for_datetime = filter_condition_by_date_time()
    return queryset_with_filter_condition(for_datetime)


def check_datetime_lookup_permission() -> None:
    """
    Check if the user has permission to access the 'date_or_time' lookup.
    """
    for_datetime = get_for_datetime_queryset()
    if not for_datetime:
        raise PermissionDenied


def get_already_created(queryset: QuerySet) -> QuerySet:
    """
    When condition instance only one, that`s mean created status
    """
    queryset = queryset.annotate(
        created_count=Count('condition')
    )
    queryset = queryset.filter(created_count__lte=1, condition__condition=Condition.ConditionChoices.CREATED)
    return queryset


def get_reason_with_empty_condition(queryset: QuerySet) -> QuerySet:
    """
    When condition is empty, return instance with described reason
    """
    latest_conditions = Condition.objects.filter(mother=OuterRef('pk')) \
                            .order_by('-created') \
                            .values('condition')[:1]

    queryset = queryset.annotate(
        latest_condition=Subquery(latest_conditions, output_field=CharField())
    )
    queryset = queryset.filter(Q(latest_condition=Condition.ConditionChoices.__empty__) | Q(latest_condition=None)
                               ).filter(condition__finished=False)

    return queryset
