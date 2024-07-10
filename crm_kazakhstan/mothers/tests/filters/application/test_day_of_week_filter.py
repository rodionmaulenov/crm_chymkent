from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from freezegun import freeze_time
from django.contrib.auth import get_user_model
from django.contrib import admin

from mothers.admin import MotherAdmin
from mothers.filters.applications import DayOfWeekFilter
from mothers.models import Mother

User = get_user_model()


class TestDayOfWeekFilter(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.factory = RequestFactory()
        self.mother_admin_instance = MotherAdmin(Mother, admin)

        # Create users with different time zones
        self.user_utc = User.objects.create_user(
            username='testuser_utc',
            password='password',
            timezone='UTC'
        )
        self.user_kiev = User.objects.create_user(
            username='testuser_est',
            password='password',
            timezone='Europe/Kiev'
        )

    @freeze_time("2024-07-08 23:00:00")
    def test_day_of_week_when_utc_monday_and_user_local_is_tuesday(self):
        # Ensure created date falls on specific days in UTC
        self.mother_monday = Mother.objects.create(name="Mother Monday")
        self.assertEqual(self.mother_monday.created.weekday(), 0)
        request = self.factory.get('/')
        request.user = self.user_utc
        filter_ = DayOfWeekFilter(request, {'created_day_of_week': '0'}, Mother, self.mother_admin_instance)
        queryset = filter_.queryset(request, Mother.objects.all())
        self.assertEqual(queryset.count(), 1)

        request = self.factory.get('/')
        request.user = self.user_kiev
        filter_ = DayOfWeekFilter(request, {'created_day_of_week': '1'}, Mother, self.mother_admin_instance)
        queryset = filter_.queryset(request, Mother.objects.all())
        self.assertEqual(queryset.count(), 1)
