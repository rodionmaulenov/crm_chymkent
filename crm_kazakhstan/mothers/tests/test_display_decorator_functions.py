import datetime
import pytz

from django.utils import timezone
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.db import models

from mothers.models import Mother
from mothers.admin import MotherAdmin

User = get_user_model()
Mother: models


class MotherAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user_with_timezone = User.objects.create_user(username='user_with_tz', password='password',
                                                           timezone='Europe/Kiev', is_superuser=True)
        self.mother_admin_instance = MotherAdmin(Mother, admin.site)

        aware_datetime_utc = timezone.make_aware(
            datetime.datetime(2023, 12, 16, 12, 0), timezone=timezone.utc
        )

        # Now use this aware_datetime_utc when creating the Mother object
        self.mother_obj = Mother.objects.create(
            name='Test Mother',
            date_create=aware_datetime_utc,
        )

    def test_date_created_for_user_with_time_zone(self):
        # Manually activate the timezone for the user
        user_timezone = pytz.timezone(self.user_with_timezone.timezone)
        timezone.activate(user_timezone)

        # Create a mock request and set the user and timezone directly
        request = self.factory.get('/')
        request.user = self.user_with_timezone
        request.timezone = self.user_with_timezone.timezone
        self.mother_admin_instance.request = request

        # Running the method
        time_created_in_local_user_time = self.mother_admin_instance.mother_date_created(self.mother_obj)
        self.assertEqual(time_created_in_local_user_time, '16 Dec 14:00',
                         msg='Time for created mother must be equal user local time not UTC')

        timezone.deactivate()
