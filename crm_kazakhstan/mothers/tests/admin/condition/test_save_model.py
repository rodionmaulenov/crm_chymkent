import datetime
import pytz

from django.db import models
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.utils import timezone
from freezegun import freeze_time

from mothers.models import Condition, Mother
from mothers.admin import ConditionAdmin

User = get_user_model()

Condition: models
Mother: models


class SaveModelMethodTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = ConditionAdmin(Condition, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser(username='admin', password='password', timezone='Europe/Kyiv')

    def test_save_model_without_scheduled_date_or_time_create(self):
        mother = Mother.objects.create(name='Mother')
        obj = Condition(mother=mother)
        self.assertIsNone(obj.pk)
        request = self.factory.get('/')
        request.user = self.superuser
        form = self.admin.get_form(request)

        self.admin.save_model(request, obj, form, change=False)

        obj.refresh_from_db()
        self.assertIsNotNone(obj.pk)

    def test_save_model_with_scheduled_date_create(self):
        mother = Mother.objects.create(name='Mother')
        obj = Condition(mother=mother, scheduled_date=datetime.date(2024, 1, 18))
        self.assertIsNone(obj.pk)
        request = self.factory.get('/')
        request.user = self.superuser
        form = self.admin.get_form(request)

        self.admin.save_model(request, obj, form, change=False)

        obj.refresh_from_db()
        self.assertIsNotNone(obj.pk)
        self.assertTrue(datetime.date(2024, 1, 18), obj.scheduled_date)

    @freeze_time("2024-01-18 12:00:00")
    def test_save_model_with_scheduled_date_and_time_create_without_local_user_time(self):
        mother = Mother.objects.create(name='Mother')
        obj = Condition(mother=mother, scheduled_date=datetime.date(2024, 1, 18),
                        scheduled_time=datetime.time(1, 0, 0))
        self.assertIsNone(obj.pk)
        request = self.factory.get('/')
        request.user = self.superuser

        form = self.admin.get_form(request)
        self.admin.save_model(request, obj, form, change=False)

        obj.refresh_from_db()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.scheduled_date, datetime.date(2024, 1, 17))
        self.assertEqual(obj.scheduled_time, datetime.time(23, 0, 0))

    @freeze_time("2024-01-18 12:00:00")
    def test_save_model_with_scheduled_date_and_time_create_with_local_user_time(self):
        kyiv_timezone = pytz.timezone('Europe/Kyiv')
        timezone.activate(kyiv_timezone)

        mother = Mother.objects.create(name='Mother')
        obj = Condition(mother=mother, scheduled_date=datetime.date(2024, 1, 18),
                        scheduled_time=datetime.time(1, 0, 0))
        self.assertIsNone(obj.pk)
        request = self.factory.get('/')
        request.user = self.superuser

        form = self.admin.get_form(request)
        self.admin.save_model(request, obj, form, change=False)

        obj.refresh_from_db()
        self.assertIsNotNone(obj.pk)

        self.assertEqual(obj.scheduled_date, datetime.date(2024, 1, 17))
        self.assertEqual(obj.scheduled_time, datetime.time(23, 0, 0))

        timezone.deactivate()

    @freeze_time("2024-01-18")
    def test_save_model_with_scheduled_date_create_with_local_user_time(self):
        kyiv_timezone = pytz.timezone('Europe/Kyiv')
        timezone.activate(kyiv_timezone)

        mother = Mother.objects.create(name='Mother')
        obj = Condition(mother=mother, scheduled_date=datetime.date(2024, 1, 18))
        self.assertIsNone(obj.pk)
        request = self.factory.get('/')
        request.user = self.superuser

        form = self.admin.get_form(request)
        self.admin.save_model(request, obj, form, change=False)

        obj.refresh_from_db()
        self.assertIsNotNone(obj.pk)

        self.assertEqual(obj.scheduled_date, datetime.date(2024, 1, 18))

        timezone.deactivate()

    @freeze_time("2024-01-18")
    def test_save_model_with_scheduled_date_create_without_local_user_time(self):
        mother = Mother.objects.create(name='Mother')
        obj = Condition(mother=mother, scheduled_date=datetime.date(2024, 1, 18))
        self.assertIsNone(obj.pk)
        request = self.factory.get('/')
        request.user = self.superuser

        form = self.admin.get_form(request)
        self.admin.save_model(request, obj, form, change=False)

        obj.refresh_from_db()
        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.scheduled_date, datetime.date(2024, 1, 18))
