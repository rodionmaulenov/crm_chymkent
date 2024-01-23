from datetime import date, time
from freezegun import freeze_time

from django.contrib.auth import get_user_model
from django.db import models
from django.test import TestCase, RequestFactory
from django.core.exceptions import PermissionDenied
from django.contrib import admin

from mothers.admin import MotherAdmin
from mothers.models import Mother, Condition

User = get_user_model()

Condition: models
Mother: models


class LookupAllowedMethodTest(TestCase):
    def setUp(self):
        self.model_admin = MotherAdmin(Mother, admin.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create_user(username='staffuser', password='staffuserpassword', is_staff=True)

    def test_lookup_not_allowed_without_date_or_time_superuser(self):
        request = self.factory.get('/mother/?lookup=date_or_time')
        request.user = self.superuser

        self.model_admin.request = request

        with self.assertRaises(PermissionDenied):
            self.model_admin.lookup_allowed('date_or_time', 'any_value')

    @freeze_time("2023-12-12 21:00:00")
    def test_lookup_allowed_with_date_or_time_super_user(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=date(2023, 12, 11),
            scheduled_time=time(20, 40, 0),
            condition='FR3',
            finished=False
        )
        request = self.factory.get('/mother/?lookup=date_or_time')
        request.user = self.superuser

        self.model_admin.request = request

        result = self.model_admin.lookup_allowed('date_or_time', 'any_value')
        self.assertTrue(result)

    @freeze_time("2023-12-12 21:00:00")
    def test_lookup_not_allowed_with_date_or_time_super_user_when_not_mothers_on_filtered_change_list(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=date(2023, 12, 13),
            scheduled_time=time(20, 40, 0),
            condition='FR3',
            finished=False
        )
        request = self.factory.get('/mother/?lookup=date_or_time')
        request.user = self.superuser

        self.model_admin.request = request

        with self.assertRaises(PermissionDenied):
            self.model_admin.lookup_allowed('date_or_time', 'any_value')

    def test_lookup_not_allowed_without_date_or_time_staff(self):
        request = self.factory.get('/mother/?lookup=date_or_time')
        request.user = self.staff_user

        self.model_admin.request = request

        with self.assertRaises(PermissionDenied):
            self.model_admin.lookup_allowed('date_or_time', 'any_value')

    @freeze_time("2023-12-12 21:00:00")
    def test_lookup_allowed_with_date_or_time_staff(self):
        mother = Mother.objects.create(name='Test Mother')
        Condition.objects.create(
            mother=mother,
            scheduled_date=date(2023, 12, 11),
            scheduled_time=time(20, 40, 0),
            condition='FR3',
            finished=False
        )
        request = self.factory.get('/mother/?lookup=date_or_time')
        request.user = self.staff_user

        self.model_admin.request = request

        result = self.model_admin.lookup_allowed('date_or_time', 'any_value')
        self.assertTrue(result)
