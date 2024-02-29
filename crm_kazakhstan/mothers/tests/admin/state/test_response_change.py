from datetime import date, time
from freezegun import freeze_time

from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.db import models
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite

from mothers.models import State, Mother
from mothers.admin import StateAdmin

User = get_user_model()

State: models
Mother: models


class ResponseChangeMethodTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        cls.mother = Mother.objects.create(name='Test Mother')

    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.condition_admin = StateAdmin(State, self.admin_site)

    def test_redirect_to_mother_change_list_with_extra_params(self):
        condition = State.objects.create(mother=self.mother, finished=False)

        query_params = '?date_create__gte=2024-01-05+00%3A00%3A00%2B02%3A00'
        relative_path = reverse('admin:mothers_state_change', args=[condition.pk])
        request = self.factory.post(relative_path)
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request.session['previous_url'] = relative_path + query_params
        request._messages = FallbackStorage(request)
        request.user = self.superuser

        response = self.condition_admin.response_change(request, condition)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin:mothers_mother_changelist'))

    def test_redirect_to_mother_change_list_without_extra_params(self):
        condition = State.objects.create(mother=self.mother, finished=False)

        relative_path = reverse('admin:mothers_state_change', args=[condition.pk])
        request = self.factory.post(relative_path)
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request._messages = FallbackStorage(request)
        request.user = self.superuser

        response = self.condition_admin.response_change(request, condition)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin:mothers_mother_changelist'))