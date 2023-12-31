import pytz

from datetime import datetime, time
from typing import Tuple, Optional

from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone, formats
from django.utils.http import urlencode
from django.utils.timezone import localtime, make_aware, activate, deactivate
from django.db import models
from django.db.models import Q, Case, When, BooleanField, Subquery, OuterRef, Value, QuerySet, Exists
from django.utils.html import format_html, mark_safe

from mothers.models import Stage, Planned, Mother, Comment, Condition

Stage: models
Planned: Stage
Mother: models
Comment: models


def get_difference_time(request, instance: Condition):
    # Convert string to a timezone object
    user_timezone = pytz.timezone(str(request.user.timezone))
    # Combine date and time strings into a datetime object
    future_local_datetime = datetime.strptime(f"{instance.scheduled_date} {instance.scheduled_time}",
                                              "%Y-%m-%d %H:%M:%S")

    # Make the datetime object timezone-aware in the user's local timezone
    future_local_aware = user_timezone.localize(future_local_datetime)

    # Convert the local timezone-aware datetime to UTC
    utc_datetime = future_local_aware.astimezone(pytz.utc)

    return utc_datetime.time()


def convert_utc_to_local(utc_date, utc_time, user_timezone_str):
    # Convert string to a timezone object
    user_timezone = pytz.timezone(str(user_timezone_str))

    # Combine UTC date and time strings into a datetime object
    utc_datetime_str = f"{utc_date} {utc_time}"
    utc_datetime_naive = datetime.strptime(utc_datetime_str, "%Y-%m-%d %H:%M:%S")

    # Make the datetime object timezone-aware in UTC
    utc_datetime_aware = pytz.utc.localize(utc_datetime_naive)

    # Convert the UTC timezone-aware datetime to user's local timezone
    local_datetime = utc_datetime_aware.astimezone(user_timezone)

    return local_datetime


def aware_datetime_from_date(search_date):
    datetime_obj = datetime.combine(search_date, datetime.min.time())
    aware_datetime = timezone.make_aware(datetime_obj, timezone=pytz.UTC)
    return aware_datetime


def by_date_or_by_datatime(request):
    list_parameters = request.GET.get('_changelist_filters', '').split('=')
    time = any(value in list_parameters for value in ['by_date', 'by_date_and_time'])
    return time


def get_specific_fields(request, inline):
    from mothers.inlines import ConditionInlineFormWithFinished, ConditionInline
    """
    Substitute Inline form on another to adding extra fields
    for ConditionListFilter instances when change ConditionInline
    """
    if isinstance(inline, ConditionInline):
        time = by_date_or_by_datatime(request)
        if time:
            inline.form = ConditionInlineFormWithFinished

    return inline


def check_queryset_logic(queryset: QuerySet) -> QuerySet:
    """
    Main logic filtering for MotherAdmin.get_queryset method
    revert only Mother instance which has last Stage instance.finished = True if exists
    else always return True.
    Then exclude Comment.banned=True
    """
    # Subquery to get the 'finished' status of the latest stage for each mother
    latest_stage_finished = Stage.objects.filter(
        mother=OuterRef('pk')
    ).order_by('-date_create').values('finished')[:1]

    # Annotate with the latest stage's 'finished' status, or False if no stage exists
    queryset = queryset.annotate(
        latest_stage_finished=Case(
            # finished status True or False on last existing Stage instance
            When(stage__isnull=False, then=Subquery(latest_stage_finished)),
            # always set True when related Stage instances not exist, because return Mother instance
            # only if latest_stage_finished equal True
            default=Value(True),
            output_field=BooleanField()
        )
    )

    # Filter based on the latest stage's 'finished' status or lack of stage
    queryset = queryset.filter(
        latest_stage_finished=True
    )

    # Exclude based on your previous conditions
    queryset = queryset.exclude(Q(comment__banned=True))

    return queryset


def first_visit_action_logic_for_queryset(queryset: QuerySet) -> Tuple[QuerySet, QuerySet]:
    """
    Processes a queryset of Mother instances, dividing it into two groups based on the criteria
    of their latest Planned instance:
    - One group includes Mothers whose latest Planned instance meets specified criteria.
    - The other group excludes those Mothers.

    Returns:
        Tuple[QuerySet, QuerySet]: A tuple of two querysets - one including and one excluding
                                   Mother instances based on the criteria.
    """

    # Subquery to find the latest Planned instance for each Mother that meets the criteria
    latest_planned_subquery = Planned.objects.filter(
        mother=OuterRef('pk'),
        plan=Planned.PlannedChoices.TAKE_TESTS,
        finished=False
    ).order_by('-id')

    # Filter Mothers based on the existence of a matching latest Planned instance
    mothers_with_latest_planned_meeting_criteria = queryset.filter(
        Exists(latest_planned_subquery[:1])
    )

    # Find Mothers who do not meet the criteria
    mothers_without_latest_planned_meeting_criteria = queryset.exclude(
        Exists(latest_planned_subquery[:1])
    )

    return mothers_with_latest_planned_meeting_criteria, mothers_without_latest_planned_meeting_criteria


def check_existence_of_latest_unfinished_plan():
    """
    Checks whether there exists at least one Mother whose most recent Planned instance
    (the latest one based on ID) meets specific criteria:
    - The plan is set to 'TAKE_TESTS', and
    - The plan is not marked as finished (finished=False).

    Returns:
        bool: True if such a Mother exists, False otherwise.
    """

    # Subquery to find the latest Planned instance for each Mother
    latest_planned_subquery = Planned.objects.filter(
        mother=OuterRef('pk'),
        plan=Planned.PlannedChoices.TAKE_TESTS,
        finished=False
    ).order_by('-id').values('id')[:1]

    # Query to find Mothers with a latest Planned instance that meets the criteria
    mothers_with_latest_planned = Mother.objects.filter(
        Exists(latest_planned_subquery)
    )

    # Check if there exists at least one Mother meeting the criteria
    exists = mothers_with_latest_planned.exists()
    return exists


def shortcut_bold_text(obj: Mother) -> format_html:
    """
    Retrieves the last condition for a `Mother` object, and returns
    its display string in a bold HTML format. The display string is truncated to 18 characters
    if it's longer than 17 characters.
    """
    # Using 'exists' to check if there is at least one finished condition
    if obj.condition_set.order_by('-id').exists():
        latest_condition = obj.condition_set.order_by('-id').first()
        for_display = latest_condition.get_condition_display()

        # Truncate and format the display text
        for_display = (for_display[:18] + '...') if len(for_display) > 17 else for_display
        return format_html('<strong>{}</strong>', for_display)


def in_user_localtime(condition: Condition, condition_time: Optional[time], request: HttpRequest) -> datetime:
    """
    Converts the scheduled date and time of a condition into the local timezone of the user.

    :return: A datetime object representing the local time for the user.
    """
    # Ensure condition has a scheduled date and condition_time is not None
    if condition.scheduled_date and condition_time:
        scheduled_datetime = datetime.combine(condition.scheduled_date, condition_time)

        # Fetch and apply user's timezone
        user_timezone_str = getattr(request.user, 'timezone', 'UTC')
        user_timezone = pytz.timezone(str(user_timezone_str))
        activate(user_timezone)
        local_scheduled_datetime = localtime(make_aware(scheduled_datetime))
        deactivate()

        return local_scheduled_datetime


def output_time_format(condition_time: Optional[time], local_scheduled_datetime: datetime) -> str:
    """
    Formats the provided datetime. If the time is midnight (00:00), it formats
    the datetime as 'Day Month'. Otherwise, it formats as 'Day Month Hour:Minute'.

    :return: A string representing the formatted datetime.
    """
    # If condition_time is None or midnight, format only the date
    if condition_time is None or condition_time == time(0, 0):
        return formats.date_format(local_scheduled_datetime, "j M")
    # Otherwise, format the date and time
    return formats.date_format(local_scheduled_datetime, "j M H:i")


def comment_plann_and_comment_finished_true(obj: Mother) -> Tuple[Planned, Comment, Condition]:
    """
    Determines if there exists either a 'Planned' instance with specific criteria
    or a non-empty 'Comment' for a given 'Mother' object or 'Condition'.

    :return: Tuple from planned, comment and condition instance
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


def last_condition_finished_and_scheduled_date_false(condition: Condition, request: HttpRequest,
                                                     condition_display: str) -> format_html:
    """
    Create url to the specific 'Condition' instance where finished and scheduled_date are None
    """

    change_url = reverse('admin:mothers_condition_change', args=[condition.id])
    current_path = request.get_full_path()
    return_path = urlencode({'_changelist_filters': current_path})
    # Define the CSS style for the link color and hover effect
    css_style = """
    <style>
        a.blue-link {
            color: green; /* Default color */
        }
        a.blue-link:hover {
            color: rgba(0, 0, 255, 0.5); /* Semi-transparent blue on hover */
        }
    </style>
    """

    # Create the link with the new class
    link_html = format_html(
        '<a href="{}?mother={}&{}" class="blue-link">{}</a>',
        change_url, condition.id, return_path, condition_display
    )

    # Return the combined HTML (style + link)
    return mark_safe(f'{css_style}{link_html}')


def last_condition_finished_false(condition: Condition, condition_display: str, request: HttpRequest) -> Optional[
    format_html]:
    """
    Retrieves the latest condition for a given 'Mother' object and formats
    its scheduled date and time.

    :return: A formatted HTML string with the condition display and its scheduled datetime.
    """

    condition_time = condition.scheduled_time or time(0, 0)
    local_scheduled_datetime = in_user_localtime(condition, condition_time, request)
    formatted_datetime = output_time_format(condition_time, local_scheduled_datetime)
    return format_html('{}/ <br> {}', condition_display, formatted_datetime)


def last_condition_finished_true(obj: Mother, condition_display: str, request: HttpRequest) -> format_html:
    """
    Generates an HTML link to add a new condition in the Django admin interface for a specific Mother object.
    This is used when the last condition is marked as finished (True).

    :return: A format_html object containing the HTML link.
    """

    condition_add_url = reverse('admin:mothers_condition_add')
    current_path = request.get_full_path()
    return_path = urlencode({'_changelist_filters': current_path})

    return format_html('<a href="{}?mother={}&{}">{}</a>',
                       condition_add_url, obj.pk, return_path, condition_display)


def get_filter_value_from_url(request: HttpRequest) -> bool:
    """
     Checks the request URL for specific 'date_or_time' filter parameters.

     This function examines the query parameters of the given HttpRequest to determine if
     the 'date_or_time' filter is set to either 'by_date' or 'by_date_and_time'. It's
     used to identify if the request corresponds to one of these specific filtered views
     in the Django admin.

     Returns:
     - bool: True if the 'date_or_time' parameter matches one of the specified filter values, False otherwise.
     """
    if 'date_or_time' in request.GET:
        filter_value = request.GET['date_or_time']
        return filter_value == 'by_date' or filter_value == 'by_date_and_time'


def meets_condition_list_filter_criteria(condition: Condition, condition_display: str,
                                         request: HttpRequest) -> format_html:
    """
    Generates a hyperlink to the admin change page for a Condition object.

    It converts the scheduled time of the condition to the user's local timezone, formats this
    datetime for display, and then constructs an anchor tag with a URL to the condition's change page.
    The anchor tag contains the condition's display string and the formatted local datetime.

    Returns:
    - format_html: An HTML string containing the hyperlink with the condition's display and localized datetime.
    """
    condition_time = condition.scheduled_time or time(0, 0)
    local_scheduled_datetime = in_user_localtime(condition, condition_time, request)
    formatted_datetime = output_time_format(condition_time, local_scheduled_datetime)
    change_condition_url = reverse('admin:mothers_condition_change', args=[condition.id])
    return format_html('<a href="{}">{}/ <br> {}</a>', change_condition_url, condition_display, formatted_datetime)
