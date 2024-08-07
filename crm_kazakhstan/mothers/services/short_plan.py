from django.db.models import Q, F, QuerySet
from django.utils import timezone


def get_mothers_with_recent_incomplete_events(mothers_queryset: QuerySet) -> QuerySet:
    """
    Retrieves Mother instances that have incomplete ScheduledEvent instances
    with a scheduled time equal to or later than the creation time of the event.
    """
    # Define conditions for non-null fields
    non_null_conditions = Q(
        age__isnull=False,
        residence__isnull=False,
        height__isnull=False,
        weight__isnull=False,
        caesarean__isnull=False,
        children__isnull=False
    )

    # Define conditions for incomplete events with valid scheduling
    recent_incomplete_events = Q(
        scheduled_event__scheduled_time__lte=F('scheduled_event__created'),
        scheduled_event__is_completed=False
    )

    # Apply filters to the queryset
    return mothers_queryset.filter(non_null_conditions, recent_incomplete_events).distinct()


def get_mother_that_event_time_has_come(qs: QuerySet) -> QuerySet:
    """
    Get queryset when time of scheduled event has come
    """
    return qs.filter(Q(scheduled_event__is_completed=False) & Q(
        scheduled_event__scheduled_time__lte=timezone.now()))
