from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.contrib.auth import get_user_model

from mothers.models import Condition, Mother
from mothers.admin import ConditionAdmin

Condition: models
Mother: models

User = get_user_model()


class ResponseAddMethodTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.condition_admin = ConditionAdmin(Condition, AdminSite())
        self.superuser = User.objects.create_superuser(username='user', password='user')
        self.staff_user = User.objects.create(username='staff_user', password='user', is_staff=True)

    def test_response_add_super_user(self):
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

    def test_response_add_staff_user(self):
        mother = Mother.objects.create(name='Mother')
        condition = Condition.objects.create(mother=mother)

        # Create a mock request with _changelist_filters in the query string
        request = self.factory.post(
            '/admin/mothers/condition/add/?_changelist_filters=/admin/mothers/mother/%3Fsomefilter%3Dvalue'
        )
        request.user = self.staff_user
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        # Simulate adding a Condition instance
        response = self.condition_admin.response_add(request, condition)

        # Expected redirect URL
        expected_url = '/admin/mothers/mother/?somefilter=value'

        # Assert that the response is a redirect to the expected URL
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_url)

    def test_response_when_condition_equal_none_superuser(self):
        mother = Mother.objects.create(name='Mother')
        Condition.objects.create(mother=mother)

        # Create a mock request with _changelist_filters in the query string
        request = self.factory.post(
            '/admin/mothers/condition/add/?_changelist_filters=/admin/mothers/mother/%3Fsomefilter%3Dvalue'
        )
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        with self.assertRaises(AttributeError):
            self.condition_admin.response_add(request, None)

    def test_response_when_condition_equal_none_staff_user(self):
        mother = Mother.objects.create(name='Mother')
        Condition.objects.create(mother=mother)

        # Create a mock request with _changelist_filters in the query string
        request = self.factory.post(
            '/admin/mothers/condition/add/?_changelist_filters=/admin/mothers/mother/%3Fsomefilter%3Dvalue'
        )
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        with self.assertRaises(AttributeError):
            self.condition_admin.response_add(request, None)
