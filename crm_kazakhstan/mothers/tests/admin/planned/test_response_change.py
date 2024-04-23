from datetime import date, time

from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages import get_messages
from django.db import models
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import admin

from mothers.models import Planned, Mother
from mothers.admin import PlannedAdmin

User = get_user_model()

Planned: models
Mother: models


class ResponseChangeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        cls.mother = Mother.objects.create(name='Test Mother')

    def setUp(self):
        self.factory = RequestFactory()
        self.condition_admin = PlannedAdmin(Planned, admin.site)
        self.mother = Mother.objects.create(name='Mother')
        self.planned = Planned.objects.create(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            note='',
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(1, 0, 0),
            created=date.today(),
            finished=False)

    def test_redirect_to_mother_change_list_with_extra_params(self):
        query_params = '?date_create__gte=2024-01-05+00%3A00%3A00%2B02%3A00'
        relative_path = reverse('admin:mothers_state_change', args=[self.planned.pk])

        request = self.factory.post(relative_path)
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request.session['previous_url'] = relative_path + query_params
        request._messages = FallbackStorage(request)
        request.user = self.superuser

        response = self.condition_admin.response_change(request, self.planned)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin:mothers_mother_changelist'))

        messages = list(get_messages(request))
        expected_message = (f'Laboratory plan successfully changed for <a href="/admin/mothers/mother/{self.mother.pk}'
                            f'/change/" ><b>Mother</b></a>')
        self.assertIn(expected_message, str(messages[0]))

    def test_redirect_to_mother_change_list_without_extra_params(self):
        relative_path = reverse('admin:mothers_state_change', args=[self.planned.pk])
        request = self.factory.post(relative_path)
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request._messages = FallbackStorage(request)
        request.user = self.superuser

        response = self.condition_admin.response_change(request, self.planned)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin:mothers_mother_changelist'))

        messages = list(get_messages(request))
        expected_message = (f'Laboratory plan successfully changed for <a href="/admin/mothers/mother/{self.mother.pk}'
                            f'/change/" ><b>Mother</b></a>')
        self.assertIn(expected_message, str(messages[0]))
