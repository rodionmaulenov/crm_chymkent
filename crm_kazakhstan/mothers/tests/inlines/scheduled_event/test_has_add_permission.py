from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone

from mothers.inlines import ScheduledEventInline
from mothers.models import Mother, ScheduledEvent

from django.contrib.admin.sites import AdminSite

User = get_user_model()


class HasAddPermissionTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # Set up a user and request
        self.user = User.objects.create_user(username='testuser', password='12345')

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

    def test_has_add_permission_no_incomplete_events(self):
        # Remove the incomplete event to test the case where there are no incomplete events
        self.event_incomplete.delete()

        request = self.factory.get('/')
        # Test that add permission is granted when there are no incomplete events
        self.assertTrue(self.inline_admin.has_add_permission(request, self.mother))

    def test_has_add_permission_with_incomplete_event(self):
        request = self.factory.get('/')
        # Test that add permission is denied when there is an incomplete event
        self.assertFalse(self.inline_admin.has_add_permission(request, self.mother))

    def test_has_add_permission_no_object(self):
        request = self.factory.get('/')
        # Test that add permission is granted when there is no obj
        self.assertTrue(self.inline_admin.has_add_permission(request, None))



