from typing import Tuple, Optional

from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.db import models
from django.utils.http import urlencode

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


def get_url_query(ind: int) -> Optional[str]:
    """
    Generates a URL for the 'Mother' admin changelist page with specific query parameters.

    Returns:
    - Optional[str]: A string containing the URL with the selected query parameters.
      If the index is outside the specified range, returns None.
    """
    if 0 <= ind <= 1:
        view_name = 'admin:mothers_mother_changelist'
        query_params = [{'date_or_time': 'by_date'}, {'date_or_time': 'by_date_and_time'}]
        return reverse(view_name) + '?' + urlencode(query_params[ind])
