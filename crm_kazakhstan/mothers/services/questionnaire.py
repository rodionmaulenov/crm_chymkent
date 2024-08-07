from django.db.models import Q, QuerySet


def get_mothers_without_incomplete_event(mothers_queryset: QuerySet) -> QuerySet:
    """
    Retrieves Mother instances that do not have incomplete ScheduledEvent or Laboratory instances.
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

    # Define exclusion conditions for incomplete events or labs
    incomplete_event_or_lab = Q(
        scheduled_event__is_completed=False
    ) | Q(
        laboratories__is_completed=False
    ) | Q(
        laboratories__doctoranswer__is_completed=False
    )

    # Filter mothers meeting the conditions and exclude those with incomplete events or labs
    return mothers_queryset.filter(non_null_conditions).exclude(incomplete_event_or_lab).distinct()
