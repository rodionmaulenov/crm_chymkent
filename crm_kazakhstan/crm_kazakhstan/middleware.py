from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store the original timezone to revert back to it after the response
        original_timezone = timezone.get_current_timezone_name()

        if request.user.is_authenticated:
            user_timezone = request.user.timezone
            timezone.activate(user_timezone)
        else:
            timezone.deactivate()

        response = self.get_response(request)

        # Revert back to the original timezone
        timezone.activate(original_timezone)

        return response
