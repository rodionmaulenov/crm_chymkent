from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from mothers.inlines import ScheduledEventInline
from mothers.models import Mother, ScheduledEvent
from django.contrib.admin.sites import AdminSite

User = get_user_model()


class GetQuerysetTest(TestCase):
    def setUp(self):
        # Set up a user and request
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.factory = RequestFactory()

        # Create a Mother instance
        self.mother = Mother.objects.create(name='Test Mother')

        # Create timezone-aware ScheduledEvent instances
        self.event_completed = ScheduledEvent.objects.create(
            mother=self.mother,
            note='Completed Event',
            scheduled_time=timezone.make_aware(timezone.datetime(2024, 7, 11, 15, 0, 0)),
            is_completed=True
        )
        self.event_incomplete = ScheduledEvent.objects.create(
            mother=self.mother,
            note='Incomplete Event',
            scheduled_time=timezone.make_aware(timezone.datetime(2024, 7, 11, 16, 0, 0)),
            is_completed=False
        )

        # Initialize the inline admin
        self.inline_admin = ScheduledEventInline(Mother, AdminSite())

    def test_get_queryset_with_add_or_change(self):
        # Simulate request with add_or_change parameter
        request = self.factory.get('/', data={'add_or_change': True})
        request.user = self.user

        # Get the queryset
        queryset = self.inline_admin.get_queryset(request)

        # Assert that only incomplete events are returned
        self.assertIn(self.event_incomplete, queryset)
        self.assertNotIn(self.event_completed, queryset)

    def test_get_queryset_without_add_or_change(self):
        request = self.factory.get('/')
        request.user = self.user

        queryset = self.inline_admin.get_queryset(request)

        # Assert that both completed and incomplete events are returned
        self.assertIn(self.event_incomplete, queryset)
        self.assertIn(self.event_completed, queryset)
