from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from mothers.models import Condition, Mother
from mothers.admin import ConditionAdmin

Condition: models
Mother: models

User = get_user_model()


class ResponseAddTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.condition_admin = ConditionAdmin(Condition, AdminSite())
        self.superuser = User.objects.create_superuser(username='user', password='user')

    def test_response_add(self):
        mother = Mother.objects.create(name='Mother')
        condition = Condition.objects.create(mother=mother)

        # Create a mock request with _changelist_filters in the query string
        request = self.factory.post(
            '/admin/mothers/condition/add/?_changelist_filters=/admin/mothers/mother/%3Fsomefilter%3Dvalue'
        )
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        # Simulate adding a Condition instance
        response = self.condition_admin.response_add(request, condition)

        # Expected redirect URL
        expected_url = '/admin/mothers/mother/?somefilter=value'

        # Assert that the response is a redirect to the expected URL
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

    def test_response_add_with_continue_editing(self):
        mother = Mother.objects.create(name='Mother')
        condition = Condition.objects.create(mother=mother)

        # Create a mock request with _continue in the POST data
        request = self.factory.post(
            '/admin/mothers/condition/add/',
            {'_continue': '1'}
        )
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        # Simulate adding a Condition instance and choosing to continue editing
        response = self.condition_admin.response_add(request, condition)

        # Assert that the response is a redirect (status code 302)
        self.assertEqual(response.status_code, 302)

        # Expected redirect URL to the edit page of the newly created object
        condition_change_url = reverse('admin:mothers_condition_change', args=[condition.pk])
        self.assertTrue(condition_change_url in response.url)

    def test_response_add_with_add_another(self):
        mother = Mother.objects.create(name='Mother')
        condition = Condition.objects.create(mother=mother)

        # Create a mock request with _addanother in the POST data
        request = self.factory.post(
            '/admin/mothers/condition/add/',
            {'_addanother': '1'}
        )
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        # Simulate adding a Condition instance and choosing to add another
        response = self.condition_admin.response_add(request, condition)

        # Expected redirect URL to the add page for a new Condition instance
        expected_url = reverse('admin:mothers_condition_add')

        # Assert that the response is a redirect to the add another URL
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

    def test_response_add_without_changelist_filters(self):
        mother = Mother.objects.create(name='Mother')
        condition = Condition.objects.create(mother=mother)

        # Create a mock request without _changelist_filters
        request = self.factory.post('/admin/mothers/condition/add/')
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        # Simulate adding a Condition instance without _changelist_filters
        response = self.condition_admin.response_add(request, condition)

        # Expected redirect URL back to the Condition list view
        expected_url = reverse('admin:mothers_condition_changelist')

        # Assert that the response is a redirect to the default URL
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

    def test_response_when_condition_equal_none(self):
        mother = Mother.objects.create(name='Mother')
        condition = Condition.objects.create(mother=mother)

        # Create a mock request with _changelist_filters in the query string
        request = self.factory.post(
            '/admin/mothers/condition/add/?_changelist_filters=/admin/mothers/mother/%3Fsomefilter%3Dvalue'
        )
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        with self.assertRaises(AttributeError):
            self.condition_admin.response_add(request, None)





