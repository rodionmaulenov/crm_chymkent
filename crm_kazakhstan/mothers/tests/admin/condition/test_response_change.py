from django.contrib.messages.storage.fallback import FallbackStorage
from django.db import models
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.admin.sites import AdminSite
from mothers.models import Condition, Mother
from mothers.admin import ConditionAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

Condition: models
Mother: models


class ResponseChangeMethodTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        cls.mother = Mother.objects.create(name='Test Mother')

    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.condition_admin = ConditionAdmin(Condition, self.admin_site)

    def test_response_change_regular_save(self):
        condition = Condition.objects.create(mother=self.mother, finished=False)

        request = self.factory.post(reverse('admin:mothers_condition_change', args=[condition.pk]), {})
        request.session = 'session'
        request._messages = FallbackStorage(request)
        request.user = self.superuser

        response = self.condition_admin.response_change(request, condition)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('admin:mothers_condition_changelist')))

    def test_response_change_with_continue(self):
        condition = Condition.objects.create(mother=self.mother, finished=False)

        change_url = reverse('admin:mothers_condition_change', args=[condition.pk])
        request = self.factory.post(change_url, {'_continue': 'Save and continue editing'})
        request.session = 'session'
        request._messages = FallbackStorage(request)
        request.user = self.superuser

        response = self.condition_admin.response_change(request, condition)

        self.assertEqual(response.status_code, 302)
        self.assertIn(change_url, response.url)

    def test_response_change_without_changelist_filters(self):
        mother = Mother.objects.create(name='Mother')
        condition = Condition.objects.create(mother=mother)

        # Create a mock request without _changelist_filters
        request = self.factory.post('/admin/mothers/condition/add/')
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        # Simulate adding a Condition instance without _changelist_filters
        response = self.condition_admin.response_change(request, condition)

        # Expected redirect URL back to the Condition list view
        expected_url = reverse('admin:mothers_condition_changelist')

        # Assert that the response is a redirect to the default URL
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

    def test_response_change_with_changelist_filters(self):
        mother = Mother.objects.create(name='Mother')
        condition = Condition.objects.create(mother=mother)

        # Create a mock request without _changelist_filters
        request = self.factory.post(
            f'/admin/mothers/condition/{condition.pk}/'
            f'change/?_changelist_filters=/admin/mothers/mother/%3Fsomefilter%3Dvalue')
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        # Simulate adding a Condition instance without _changelist_filters
        response = self.condition_admin.response_change(request, condition)

        # Expected redirect URL back to the Condition list view
        expected_url = '/admin/mothers/mother/?somefilter=value'

        # Assert that the response is a redirect to the default URL
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)
