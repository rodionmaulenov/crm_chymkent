from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.db import models
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite

from mothers.models import Mother
from mothers.admin import MotherAdmin

User = get_user_model()

Mother: models


class ResponseChangeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        cls.mother = Mother.objects.create(name='Test Mother')

    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.condition_admin = MotherAdmin(Mother, self.admin_site)

    def test_redirect_on_mother_change_list(self):
        request = self.factory.post(reverse('admin:mothers_mother_change', args=[self.mother.pk]))
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request._messages = FallbackStorage(request)
        request.user = self.superuser

        response = self.condition_admin.response_change(request, self.mother)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('admin:mothers_mother_changelist')))

    def test_redirect_on_mother_change_list_when_params_exists(self):
        query_params = '?date_create__range__gte=2023-02-01&date_create__range__lte=2024-02-15'
        relative_path = reverse('admin:mothers_mother_change', args=[self.mother.pk])
        request = self.factory.post(relative_path + query_params)
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request._messages = FallbackStorage(request)
        request.user = self.superuser

        response = self.condition_admin.response_change(request, self.mother)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin:mothers_mother_changelist'))

    def test_redirect_on_filtered_change_list_when_changelist_filters_exists(self):
        query_params = ('?_changelist_filters=date_or_time%3Dby_date_and_time')
        relative_path = reverse('admin:mothers_mother_change', args=[self.mother.pk])
        request = self.factory.post(relative_path + query_params)
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request._messages = FallbackStorage(request)
        request.user = self.superuser

        response = self.condition_admin.response_change(request, self.mother)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin:mothers_mother_changelist') + '?date_or_time=by_date_and_time')
