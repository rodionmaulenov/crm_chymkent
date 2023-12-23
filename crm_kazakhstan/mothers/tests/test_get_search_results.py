from datetime import datetime

from django.db import models
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from freezegun import freeze_time

from mothers.admin import MotherAdmin
from mothers.models import Mother
from mothers.services import aware_datetime_from_date

User = get_user_model()
Mother: models


class GetSearchResultsTest(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.admin = MotherAdmin(Mother, self.site)
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser('admin', 'admin@example.com', 'password')

        # Use timezone-aware datetime objects
        past_datetime = aware_datetime_from_date(datetime(2020, 11, 1))
        recent_datetime = aware_datetime_from_date(datetime(2023, 12, 1))
        date_create = aware_datetime_from_date(datetime(2023, 12, 2))

        self.past_model = Mother.objects.create(name='Test1', date_create=past_datetime)
        self.recent_model = Mother.objects.create(name='Test2', date_create=recent_datetime)
        self.mother3 = Mother.objects.create(name='Test3', date_create=date_create)

    @freeze_time("2023-12-10")
    def test_get_search_results_by_date(self):
        request = self.factory.get('/')
        request.user = self.user
        search_term = '2023-11-02'

        queryset, _ = self.admin.get_search_results(request, Mother.objects.all(), search_term)

        self.assertNotIn(self.past_model, queryset)
        self.assertIn(self.recent_model, queryset)

    @freeze_time("2023-12-10")
    def test_get_search_results_by_reverse_date(self):
        request = self.factory.get('/')
        request.user = self.user
        search_term = '02-11-2023'

        queryset, _ = self.admin.get_search_results(request, Mother.objects.all(), search_term)

        self.assertNotIn(self.past_model, queryset)
        self.assertIn(self.recent_model, queryset)

    @freeze_time("2023-12-10")
    def test_get_search_results_by_reverse_date(self):
        request = self.factory.get('/')
        request.user = self.user
        search_term = '02'

        queryset, _ = self.admin.get_search_results(request, Mother.objects.all(), search_term)
        self.assertEqual(1, len(queryset))

    @freeze_time("2023-12-10")
    def test_get_search_results_by_reverse_date(self):
        request = self.factory.get('/')
        request.user = self.user
        search_term = '02-11'

        queryset, _ = self.admin.get_search_results(request, Mother.objects.all(), search_term)
        self.assertEqual(2, len(queryset))

