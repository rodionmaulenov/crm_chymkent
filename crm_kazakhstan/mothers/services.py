from datetime import datetime
import pytz
from django.utils import timezone

from mothers.models import Condition


def get_difference_time(request, instance: Condition):
    # Step 1: Get aware datetime in UTC
    utc_aware = timezone.now()

    # Step 2: Get aware datetime based on the user's timezone
    user_timezone = pytz.timezone(str(request.user.timezone))
    local_time_aware = utc_aware.astimezone(user_timezone)

    # Step 3: Get aware datetime for the user's input time on the current date
    user_input_datetime_aware = timezone.make_aware(
        datetime.combine(utc_aware.date(), instance.scheduled_time),
        user_timezone
    )

    # step 4: Calculate the time difference between user input time and local time
    time_difference_input_and_local = user_input_datetime_aware - local_time_aware

    # step 5: Calculate the time that the server should save
    server_time_must_be_aware = utc_aware + time_difference_input_and_local

    return server_time_must_be_aware


def aware_datetime_from_date(search_date):
    datetime_obj = datetime.combine(search_date, datetime.min.time())
    aware_datetime = timezone.make_aware(datetime_obj, timezone=pytz.UTC)
    return aware_datetime

