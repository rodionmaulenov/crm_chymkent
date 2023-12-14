from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            user_timezone = request.user.timezone
            timezone.activate(user_timezone)

        return response
