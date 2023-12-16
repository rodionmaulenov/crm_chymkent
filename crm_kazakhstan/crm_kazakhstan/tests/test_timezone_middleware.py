from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone

from crm_kazakhstan.middleware import TimezoneMiddleware

User = get_user_model()


class TimezoneMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user_with_timezone = User.objects.create_user(username='user_with_tz', password='password')
        self.user_with_timezone.timezone = 'Europe/Kiev'
        self.user_with_timezone.save()

        self.user_without_timezone = User.objects.create_user(username='user_without_tz', password='password')

        self.middleware = TimezoneMiddleware(lambda x: x)

    def test_timezone_set_for_authenticated_user(self):
        request = self.factory.get('/')
        request.user = self.user_with_timezone

        self.middleware(request)
        self.assertEqual(request.applied_timezone, 'Europe/Kiev')

    def test_timezone_not_set_for_unauthenticated_user(self):
        request = self.factory.get('/')
        request.user = self.user_without_timezone

        self.middleware(request)
        self.assertEqual(request.applied_timezone, 'UTC')

    def test_timezone_reverted_after_request(self):
        original_timezone = timezone.get_current_timezone_name()

        request = self.factory.get('/')
        request.user = self.user_with_timezone

        self.middleware(request)

        # Test that the original timezone is restored after the middleware
        self.assertEqual(timezone.get_current_timezone_name(), original_timezone)


