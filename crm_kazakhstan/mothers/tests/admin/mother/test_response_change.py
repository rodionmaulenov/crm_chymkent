from datetime import date, time
from freezegun import freeze_time

from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.db import models
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite

from mothers.models import Condition, Mother
from mothers.admin import MotherAdmin

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
        self.condition_admin = MotherAdmin(Mother, self.admin_site)

    def test_redirect_to_mother_change_list_when_change_without_filtered_previous_url(self):
        request = self.factory.post(reverse('admin:mothers_mother_change', args=[self.mother.pk]))
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request._messages = FallbackStorage(request)
        request.user = self.superuser

        response = self.condition_admin.response_change(request, self.mother)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('admin:mothers_mother_changelist')))

    def test_redirect_to_mother_change_list_when_change_with_filtered_previous_url(self):
        query_params = '?date_create__gte=2024-01-05+00%3A00%3A00%2B02%3A00'
        relative_path = reverse('admin:mothers_mother_change', args=[self.mother.pk])
        request = self.factory.post(relative_path)
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request.session['previous_url'] = relative_path + query_params
        request._messages = FallbackStorage(request)
        request.user = self.superuser

        response = self.condition_admin.response_change(request, self.mother)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, relative_path + query_params)

    @freeze_time("2024-12-12 20:00:00")
    def test_redirect_on_same_filtered_change_list_when_not_another_scheduled_date_and_time_exists_and_finished_false(
            self):
        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 12, 12),
                                             scheduled_time=time(20, 0, 0))

        query_params = '?date_or_time=by_date_and_time'
        relative_path = reverse('admin:mothers_mother_change', args=[self.mother.pk])
        request = self.factory.post(relative_path)
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request.session['previous_url'] = relative_path + query_params
        request._messages = FallbackStorage(request)
        request.user = self.superuser

        response = self.condition_admin.response_change(request, self.mother)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, relative_path + query_params)

    @freeze_time("2024-12-12 20:00:00")
    def test_redirect_on_filtered_change_list_with_extra_query_when_not_another_scheduled_date_and_time_exists_and_finished_false(
            self):
        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 12, 12),
                                             scheduled_time=time(20, 0, 0))

        query_params = ('?date_create__gte=2024-01-05+00%3A00%3A00%2B02%3A00&'
                        'date_create__lt=2024-01-13+00%3A00%3A00%2B02%3A00&date_or_time=by_date_and_time')
        relative_path = reverse('admin:mothers_mother_change', args=[self.mother.pk])
        request = self.factory.post(relative_path)
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request.session['previous_url'] = relative_path + query_params
        request._messages = FallbackStorage(request)
        request.user = self.superuser

        response = self.condition_admin.response_change(request, self.mother)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, relative_path + query_params)

    @freeze_time("2024-12-12 20:20:00")
    def test_redirect_to_the_same_filtered_change_list_when_another_scheduled_date_and_time_exists_and_finished_false(
            self):
        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 12, 12),
                                 scheduled_time=time(20, 0, 0))
        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 12, 12),
                                             scheduled_time=time(20, 0, 0))

        query_params = '?date_or_time=by_date_and_time'
        relative_path = reverse('admin:mothers_mother_change', args=[self.mother.pk])
        request = self.factory.post(relative_path)
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request.session['previous_url'] = relative_path + query_params
        request._messages = FallbackStorage(request)
        request.user = self.superuser

        response = self.condition_admin.response_change(request, self.mother)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, relative_path + query_params)

    @freeze_time("2024-12-12 20:20:00")
    def test_redirect_to_the_same_filtered_change_list_when_another_scheduled_date_and_time_exists_and_finished_false_(
            self):
        """
        Additionally to filtered query base on date_and_time in previous url has another filtered query
        """
        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 12, 12),
                                 scheduled_time=time(20, 0, 0))
        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 12, 12),
                                             scheduled_time=time(20, 0, 0))

        query_params = ('?date_create__gte=2024-01-05+00%3A00%3A00%2B02%3A00&'
                        'date_create__lt=2024-01-13+00%3A00%3A00%2B02%3A00&date_or_time=by_date_and_time')
        relative_path = reverse('admin:mothers_mother_change', args=[self.mother.pk])
        request = self.factory.post(relative_path)
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request.session['previous_url'] = relative_path + query_params
        request._messages = FallbackStorage(request)
        request.user = self.superuser

        response = self.condition_admin.response_change(request, self.mother)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, relative_path + query_params)

    @freeze_time("2024-12-12 20:20:00")
    def test_redirect_mother_changelist_when_not_another_scheduled_date_time_exists_and_finished_true(
            self):
        Condition.objects.create(mother=self.mother, finished=True, scheduled_date=date(2024, 12, 12),
                                             scheduled_time=time(20, 0, 0))

        query_params = '?date_or_time=by_date_and_time'
        relative_path = reverse('admin:mothers_mother_change', args=[self.mother.pk])
        request = self.factory.post(relative_path)
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request.session['previous_url'] = relative_path + query_params
        request._messages = FallbackStorage(request)
        request.user = self.superuser

        response = self.condition_admin.response_change(request, self.mother)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin:mothers_mother_changelist'))

    @freeze_time("2024-12-12 20:20:00")
    def test_redirect_mother_changelist_when_not_another_scheduled_date_time_exists_and_finished_true_(
            self):
        """
         Additionally to filtered query base on date_and_time in previous url has another filtered query
        """
        condition = Condition.objects.create(mother=self.mother, finished=True, scheduled_date=date(2024, 12, 12),
                                             scheduled_time=time(20, 0, 0))

        query_params = ('?date_create__gte=2024-01-05+00%3A00%3A00%2B02%3A00&'
                        'date_create__lt=2024-01-13+00%3A00%3A00%2B02%3A00&date_or_time=by_date_and_time')
        relative_path = reverse('admin:mothers_mother_change', args=[self.mother.pk])
        request = self.factory.post(relative_path)
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request.session['previous_url'] = relative_path + query_params
        request._messages = FallbackStorage(request)
        request.user = self.superuser

        response = self.condition_admin.response_change(request, self.mother)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin:mothers_mother_changelist'))

    @freeze_time("2024-12-12 20:20:00")
    def test_redirect_to_the_same_filtered_change_list_when_another_scheduled_date_time_exists_and_finished_stay_true(
            self):
        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 12, 12),
                                 scheduled_time=time(20, 0, 0))
        condition = Condition.objects.create(mother=self.mother, finished=True, scheduled_date=date(2024, 12, 12),
                                             scheduled_time=time(20, 0, 0))

        query_params = '?date_or_time=by_date_and_time'
        relative_path = reverse('admin:mothers_mother_change', args=[self.mother.pk])
        request = self.factory.post(relative_path)
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request.session['previous_url'] = relative_path + query_params
        request._messages = FallbackStorage(request)
        request.user = self.superuser

        response = self.condition_admin.response_change(request, self.mother)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, relative_path + query_params)

    @freeze_time("2024-12-12 20:20:00")
    def test_redirect_to_the_same_filtered_change_list_when_another_scheduled_date_time_exists_and_finished_stay_true_(
            self):
        """
        Additionally to filtered query base on date_and_time in previous url has another filtered query
        """
        Condition.objects.create(mother=self.mother, finished=False, scheduled_date=date(2024, 12, 12),
                                 scheduled_time=time(20, 0, 0))
        Condition.objects.create(mother=self.mother, finished=True, scheduled_date=date(2024, 12, 12),
                                             scheduled_time=time(20, 0, 0))

        query_params = ('?date_create__gte=2024-01-05+00%3A00%3A00%2B02%3A00&'
                        'date_create__lt=2024-01-13+00%3A00%3A00%2B02%3A00&date_or_time=by_date_and_time')
        relative_path = reverse('admin:mothers_mother_change', args=[self.mother.pk])
        request = self.factory.post(relative_path)
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request.session['previous_url'] = relative_path + query_params
        request._messages = FallbackStorage(request)
        request.user = self.superuser

        response = self.condition_admin.response_change(request, self.mother)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, relative_path + query_params)
