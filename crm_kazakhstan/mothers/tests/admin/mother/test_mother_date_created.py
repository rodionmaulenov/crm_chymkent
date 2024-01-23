import datetime

from django.utils import timezone
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.db import models
from freezegun import freeze_time

from mothers.models import Mother
from mothers.admin import MotherAdmin

User = get_user_model()
Mother: models


class MotherDateCreateTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user_with_timezone = User.objects.create_user(username='user_with_tz', password='password',
                                                           timezone='Europe/Kiev', is_superuser=True)
        self.mother_admin_instance = MotherAdmin(Mother, admin.site)

    @freeze_time("2023-12-12 16:00:00")
    def test_date_created_for_user_with_time_zone(self):
        request = self.factory.get('/')
        request.user = self.user_with_timezone
        self.mother_admin_instance.request = request

        self.mother_obj = Mother.objects.create(
            name='Test Mother',
            date_create=timezone.make_aware(
                datetime.datetime(2023, 12, 12, 16, 0, 0), timezone=timezone.utc)
        )

        time_created_in_local_user_time = self.mother_admin_instance.date_created(self.mother_obj)
        self.assertEqual(time_created_in_local_user_time, '12 Dec 18:00')
