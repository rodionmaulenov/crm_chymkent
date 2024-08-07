from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from mothers.models import Mother
from mothers.admin import QuestionnaireAdmin
from django.contrib.admin.sites import AdminSite

User = get_user_model()


class ScheduledEventTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # Set up a user and request
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Create a Mother instance
        self.mother = Mother.objects.create(name='Test Mother')

        # Create the admin instance
        self.admin = QuestionnaireAdmin(Mother, AdminSite())

    def test_scheduled_event_with_permissions(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename='view_questionnaire')
        )
        # Simulate request with necessary permissions
        request = self.factory.get('/', {'add_or_change': 'add'})
        request.user = self.user
        self.admin.request = request

        # Call the method and verify the output
        result = self.admin.scheduled_event(self.mother)
        expected_url = 'add event'
        self.assertEqual(result, expected_url)

    def test_scheduled_event_not_only_view_permissions(self):
        self.user.user_permissions.set(
            [Permission.objects.get(codename='view_questionnaire'),
             Permission.objects.get(codename='change_questionnaire')]
        )

        # Simulate request without necessary permissions
        request = self.factory.get('/', {'add_or_change': 'add'})
        request.user = self.user
        self.admin.request = request

        # Call the method and verify the output
        result = self.admin.scheduled_event(self.mother)
        expected = f'<a href="/admin/mothers/questionnaire/{self.mother.pk}/change/?add_or_change=add">add event</a>'
        self.assertEqual(result, expected)
