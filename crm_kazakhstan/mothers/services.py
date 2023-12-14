from datetime import datetime, timedelta
import pytz

from mothers.models import Condition


def get_difference_time(request, instance: Condition):
    # get naive datetime
    utc = datetime.now()
    # Step 1: Get naive datetime bases on specific timezone
    time_zone = pytz.timezone(str(request.user.timezone))
    local_time = datetime.now(time_zone)
    local_time = datetime.combine(local_time.date(), local_time.time())

    # Step 2: Get naive date additionally with user input time
    user_input_date = datetime.combine(utc.date(), instance.scheduled_time)

    # step 3: Get difference between user input time and local time
    time_difference_input_and_local = user_input_date - local_time

    # step 4: Total seconds remain after subtraction
    total_seconds = time_difference_input_and_local.total_seconds()

    # Calculate hours and minutes
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)

    # Step 5: Server time increase on time_difference_local_and_server
    server_time_must_be = utc + timedelta(hours=hours, minutes=minutes)

    return server_time_must_be.time()
