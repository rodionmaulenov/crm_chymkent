from zoneinfo import reset_tzpath

from django.db.models import Q, QuerySet
from django.utils import timezone


def mothers_which_on_laboratory_stage(Mothers_queryset: QuerySet) -> QuerySet:
    """
    Retrieves Mother instances which planned laboratory visit or wait doctor answer.
    """

    queryset = Mothers_queryset.filter(
        Q(laboratories__is_completed=False) |
        Q(laboratories__doctoranswer__is_completed=False)
    )

    return queryset


def filter_for_pagination_queryset(Mothers_queryset: QuerySet, request) -> QuerySet:
    # When is it time to visit laboratory
    time_new_visit = Mothers_queryset.filter(Q(laboratories__is_completed=False) &
                                             Q(laboratories__is_came__exact='') &
                                             Q(laboratories__scheduled_time__lte=timezone.now()))
    # When not visited laboratory at all
    not_visit = Mothers_queryset.filter(Q(laboratories__is_completed=False) &
                                        Q(laboratories__is_came=False) &
                                        Q(laboratories__scheduled_time__lte=timezone.now()))

    # When visited laboratory
    already_visit = Mothers_queryset.filter(Q(laboratories__is_completed=False) &
                                            Q(laboratories__is_came=True) &
                                            Q(laboratories__scheduled_time__lte=timezone.now()))

    if request.GET.get("time_new_visit") == 'new_visit':
        return time_new_visit
    if request.GET.get("time_new_visit") == 'not_visit':
        return not_visit
    if request.GET.get("time_new_visit") == 'visit':
        return already_visit

    return Mothers_queryset
