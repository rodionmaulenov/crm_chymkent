import pytz

from datetime import datetime

from django.utils import timezone
from django.db import models
from django.db.models import Q, Case, When, BooleanField, Subquery, OuterRef, Value, QuerySet

from mothers.models import Stage
from mothers.models.one_to_many import Condition

Stage: models


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
