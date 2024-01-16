from datetime import time, date
from freezegun import freeze_time

from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.contrib.auth import get_user_model

from mothers.models import Condition, Mother
from mothers.admin import ConditionAdmin

Mother: models
Condition: models

User = get_user_model()


class GetFormMethodTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.condition_admin = ConditionAdmin(model=Condition, admin_site=self.admin_site)
        self.superuser_without_timezone = User.objects.create_superuser(username='test_name', password='password')
        self.superuser = User.objects.create_superuser(username='test_name1', password='password',
                                                       timezone='Europe/Kyiv')

    @freeze_time("2023-12-12 10:00:00")
    def test_change_with_date_time_when_user_local_time_bigger_on_two_hours(self):
        request = self.factory.get('/')
        request.user = self.superuser

        # Get the form class using get_form without passing the instance
        form_class = self.condition_admin.get_form(request, obj=None)

        # Create a condition instance
        mother = Mother.objects.create(name='Test Mother')
        condition = Condition.objects.create(mother=mother, scheduled_date=date(2023, 12, 12),
                                             scheduled_time=time(10, 0))

        # Instantiate the form with the condition instance
        form = form_class(instance=condition)

        # Print and check the initial data
        self.assertEqual(form.initial['scheduled_time'], time(12, 0))

    @freeze_time("2023-12-12 23:00:00")
    def test_change_with_date_time_when_user_local_time_bigger_on_two_hours_example2(self):
        request = self.factory.get('/')
        request.user = self.superuser

        # Get the form class using get_form without passing the instance
        form_class = self.condition_admin.get_form(request, obj=None)

        # Create a condition instance
        mother = Mother.objects.create(name='Test Mother')
        condition = Condition.objects.create(mother=mother, scheduled_date=date(2023, 12, 12),
                                             scheduled_time=time(23, 0))

        # Instantiate the form with the condition instance
        form = form_class(instance=condition)

        # Print and check the initial data
        self.assertEqual(form.initial['scheduled_date'], date(2023, 12, 13))
        self.assertEqual(form.initial['scheduled_time'], time(1, 0))

    @freeze_time("2023-12-12 10:00:00")
    def test_change_with_date_time_without_user_local_time_bigger_on_two_hours(self):
        request = self.factory.get('/')
        request.user = self.superuser_without_timezone

        # Get the form class using get_form without passing the instance
        form_class = self.condition_admin.get_form(request, obj=None)

        # Create a condition instance
        mother = Mother.objects.create(name='Test Mother')
        condition = Condition.objects.create(mother=mother, scheduled_date=date(2023, 12, 12),
                                             scheduled_time=time(10, 0))

        # Instantiate the form with the condition instance
        form = form_class(instance=condition)

        # Print and check the initial data
        self.assertEqual(form.initial['scheduled_time'], time(10, 0))
