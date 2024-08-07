from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model

from mothers.inlines import ScheduledEventInline
from mothers.models import Mother, ScheduledEvent

from django.contrib.admin.sites import AdminSite

User = get_user_model()


class HasChangePermissionTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # Set up a user and request
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Create a Mother instance
        self.mother = Mother.objects.create(name='Test Mother')

        # Initialize the inline admin
        self.inline_admin = ScheduledEventInline(Mother, AdminSite())

    def test_has_change_permission_with_add_or_change(self):
        # Simulate request with add_or_change parameter
        request = self.factory.get('/', {'add_or_change': 'true'})
        request.user = self.user

        # Test that change permission is granted when add_or_change parameter is present
        self.assertTrue(self.inline_admin.has_change_permission(request, self.mother))

    def test_has_change_permission_without_add_or_change(self):
        # Simulate request without add_or_change parameter
        request = self.factory.get('/')
        request.user = self.user

        # Test that change permission is denied when add_or_change parameter is not present
        self.assertFalse(self.inline_admin.has_change_permission(request, self.mother))

    def test_has_change_permission_no_object(self):
        # Simulate request without add_or_change parameter
        request = self.factory.get('/')
        request.user = self.user

        # Test that change permission is denied when add_or_change parameter is not present and obj is None
        self.assertFalse(self.inline_admin.has_change_permission(request, None))
