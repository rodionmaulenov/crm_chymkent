from datetime import date, time

from freezegun import freeze_time

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

        request = self.factory.post(reverse('admin:mothers_condition_change', args=[condition.pk]))
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
        request = self.factory.post('/admin/mothers/condition/change/')
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

    def test_redirect_finished_condition_with_date_and_not_another_condition_instances(self):
        condition = Condition.objects.create(mother=self.mother, finished=True, scheduled_date='2024-01-09')

        # Simulate a POST request to change the condition to finished
        request = self.factory.get(reverse('admin:mothers_condition_change', args=[condition.pk]))
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        request.user = self.superuser

        response = self.condition_admin.response_change(request, condition)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('admin:mothers_mother_changelist')))

    def test_redirect_finished_condition_with_datetime_and_not_another_condition_instances(self):
        condition = Condition.objects.create(mother=self.mother, finished=True, scheduled_date='2024-01-09',
                                             scheduled_time='20:00:09')

        # Simulate a POST request to change the condition to finished
        request = self.factory.get(reverse('admin:mothers_condition_change', args=[condition.pk]))
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        request.user = self.superuser

        response = self.condition_admin.response_change(request, condition)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('admin:mothers_mother_changelist')))

    @freeze_time("2024-12-12 20:30:00")
    def test_redirect_finished_condition_with_datetime_and_another_condition(self):
        mother = Mother.objects.create(name="for test")
        condition = Condition.objects.create(mother=mother, finished=True, scheduled_date=date(2024, 1, 9),
                                             scheduled_time=time(10, 0, 0))

        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 1, 9),
                                 scheduled_time=time(10, 0, 0))

        # Simulate a POST request to change the condition to finished
        request = self.factory.post(reverse('admin:mothers_condition_change', args=[condition.pk]))
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        response = self.condition_admin.response_change(request, condition)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/mothers/mother/?date_or_time=by_date_and_time")

    @freeze_time("2024-12-12 20:30:00")
    def test_redirect_finished_condition_with_date_and_another_condition(self):
        mother = Mother.objects.create(name="for test")
        condition = Condition.objects.create(mother=mother, finished=True, scheduled_date=date(2024, 1, 9))

        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 1, 9))

        # Simulate a POST request to change the condition to finished
        request = self.factory.post(reverse('admin:mothers_condition_change', args=[condition.pk]))
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        response = self.condition_admin.response_change(request, condition)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/mothers/mother/?date_or_time=by_date")

    @freeze_time("2024-12-12 20:30:00")
    def test_redirect_finished_false_and_scheduled_date(self):
        condition = Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 1, 9))

        # Simulate a POST request to change the condition to finished
        request = self.factory.post(reverse('admin:mothers_condition_change', args=[condition.pk]))
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        response = self.condition_admin.response_change(request, condition)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/mothers/mother/?date_or_time=by_date")

    @freeze_time("2024-12-12 20:30:00")
    def test_redirect_finished_false_and_scheduled_date_and_scheduled_time(self):
        condition = Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 1, 9),
                                             scheduled_time=time(10, 0, 0))

        request = self.factory.post(reverse('admin:mothers_condition_change', args=[condition.pk]))
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        response = self.condition_admin.response_change(request, condition)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/mothers/mother/?date_or_time=by_date_and_time")

    @freeze_time("2023-12-12 20:30:00")
    def test_redirect_finished_false_and_scheduled_date_on_changelist(self):
        condition = Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 1, 9))

        # Simulate a POST request to change the condition to finished
        request = self.factory.post(reverse('admin:mothers_condition_change', args=[condition.pk]))
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        response = self.condition_admin.response_change(request, condition)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/mothers/mother/")

    @freeze_time("2023-12-12 20:30:00")
    def test_redirect_finished_false_and_scheduled_date_and_scheduled_time_on_changelist(self):
        condition = Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 1, 9),
                                             scheduled_time=time(10, 0, 0))

        request = self.factory.post(reverse('admin:mothers_condition_change', args=[condition.pk]))
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        response = self.condition_admin.response_change(request, condition)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/mothers/mother/")
