from typing import Tuple

from django.db.models import Q
from django.http import HttpRequest, HttpResponseRedirect
from django.utils import timezone
from django.db import models

from mothers.models import Mother

Mother: models


def filter_condition_by_date_time() -> Tuple[Q, Q]:
    """
    Generates query filters for 'Condition' objects based on the current date and time.

    Returns two query filters:
    - for_date: Filters for conditions scheduled on or before the current date
                with no specific time, and not finished.
    - for_datetime: Filters for conditions either scheduled for a date earlier
                    than today or for today with a time earlier than or equal
                    to the current time, and not finished.

    :return: A tuple containing two query filters (for_date, for_datetime).
    """

    current_date = timezone.now().date()
    current_time = timezone.now().time()

    for_datetime = (Q(condition__scheduled_date=current_date, condition__scheduled_time__lte=current_time) |
                    Q(condition__scheduled_date__lt=current_date, condition__scheduled_time__isnull=False)
                    ) & Q(condition__finished=False)

    for_date = (Q(condition__scheduled_date__lte=current_date, condition__scheduled_time__isnull=True)
                ) & Q(condition__finished=False)

    return for_date, for_datetime


def queryset_with_filter_condition(for_date: Q, for_datetime: Q) -> Tuple[bool, bool]:
    """
    Evaluates whether there are any Mother objects that match the given query filters.
    Args:
    - for_date (Q): A Django Q object representing the filter condition for dates.
    - for_datetime (Q): A Django Q object representing the filter condition for date and time.

    Returns:
    - Tuple[bool, bool]: A tuple containing two boolean values. The first value indicates whether
      any Mother objects meet the 'for_date' condition, and the second value indicates whether any
      meet the 'for_datetime' condition.
    """
    exists_for_date = Mother.objects.filter(for_date).exists()
    exists_for_datetime = Mother.objects.filter(for_datetime).exists()
    return exists_for_date, exists_for_datetime


def is_filtered_condition_met(previous_url: str, for_date: bool, for_datetime: bool) -> bool:
    """
    Checks if the previous URL is a filtered condition and if the respective queryset is not empty.
    """

    if previous_url:
        not_filtered_list_page = any(previous_url.endswith(value) for value in ['by_date', 'by_date_and_time'])
        previous_url_without_filtered_change_list = previous_url and not not_filtered_list_page

        if previous_url_without_filtered_change_list:
            return True
        if previous_url.endswith('by_date') and for_date:
            return True
        if previous_url.endswith('by_date_and_time') and for_datetime:
            return True
        return False


def redirect_to_appropriate_url(request: HttpRequest, previous_url: str, default_url: str) -> HttpResponseRedirect:
    """
    Redirects to the appropriate URL based on the previous URL or defaults to the provided URL.
    """
    if previous_url:
        del request.session['previous_url']
        return HttpResponseRedirect(previous_url)
    return HttpResponseRedirect(default_url)
