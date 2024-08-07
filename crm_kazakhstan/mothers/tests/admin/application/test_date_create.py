from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib import admin
import pytz
from freezegun import freeze_time

from mothers.admin import MotherAdmin
from mothers.filters.applications import convert_utc_to_local
from mothers.models import Mother

User = get_user_model()


@freeze_time("2024-07-08 23:00:00")
class TestDayOfWeekFilter(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.factory = RequestFactory()
        self.mother_admin = MotherAdmin(Mother, admin)

        # Create a sample Mother instance
        now = timezone.now().astimezone(pytz.utc)
        self.mother = Mother.objects.create(name="Test Mother", created=now)

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

    def test_date_create_user_utc(self):
        # Attach the request to the admin instance
        request = self.factory.get('/')
        request.user = self.user_utc
        self.mother_admin.request = request

        # Call the date_create method and check the output
        formatted_date = self.mother_admin.date_create(self.mother)
        visible_date = "<strong>Monday 23:00</strong>"
        expected_date = convert_utc_to_local(request, self.mother.created).strftime("%A %H:%M")
        expected_html = f"<strong>{expected_date}</strong>"

        self.assertEqual(visible_date, expected_html)
        self.assertEqual(formatted_date, expected_html)

    def test_date_create_user_local_time(self):
        # Attach the request to the admin instance
        request = self.factory.get('/')
        request.user = self.user_kiev
        self.mother_admin.request = request

        # Call the date_create method and check the output
        formatted_date = self.mother_admin.date_create(self.mother)
        visible_date = "<strong>Tuesday 02:00</strong>"
        expected_date = convert_utc_to_local(request, self.mother.created).strftime("%A %H:%M")
        expected_html = f"<strong>{expected_date}</strong>"

        self.assertEqual(visible_date, expected_html)
        self.assertEqual(formatted_date, expected_html)
