from datetime import time, date
from freezegun import freeze_time

from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.contrib.auth import get_user_model

from mothers.models import State, Mother
from mothers.admin import StateAdmin

Mother: models
State: models

User = get_user_model()


class GetFormMethodTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.condition_admin = StateAdmin(State, self.admin_site)
        self.superuser_without_timezone = User.objects.create_superuser(username='test_name', password='password')
        self.superuser = User.objects.create_superuser(username='test_name1', password='password',
                                                       timezone='Europe/Kyiv')

    @freeze_time("2023-12-12 10:00:00")
    def test_change_with_date_time_when_user_local_time_bigger_on_two_hours(self):
        request = self.factory.get('/')
        request.user = self.superuser

        form_class = self.condition_admin.get_form(request, obj=None)

        mother = Mother.objects.create(name='Test Mother')
        condition = State.objects.create(mother=mother, scheduled_date=date(2023, 12, 12),
                                         scheduled_time=time(10, 0))

        # Instantiate the form with the condition instance
        form = form_class(instance=condition)

        self.assertEqual(form.initial['scheduled_time'], time(12, 0))

    @freeze_time("2023-12-12 23:00:00")
    def test_change_with_date_time_when_user_local_time_bigger_on_two_hours_example2(self):
        request = self.factory.get('/')
        request.user = self.superuser

        form_class = self.condition_admin.get_form(request, obj=None)

        mother = Mother.objects.create(name='Test Mother')
        condition = State.objects.create(mother=mother, scheduled_date=date(2023, 12, 12),
                                         scheduled_time=time(23, 0))

        form = form_class(instance=condition)

        self.assertEqual(form.initial['scheduled_date'], date(2023, 12, 13))
        self.assertEqual(form.initial['scheduled_time'], time(1, 0))

    @freeze_time("2023-12-12 10:00:00")
    def test_change_with_date_time_without_user_local_time_bigger_on_two_hours(self):
        request = self.factory.get('/')
        request.user = self.superuser_without_timezone

        # Get the form class using get_form without passing the instance
        form_class = self.condition_admin.get_form(request, obj=None)

        mother = Mother.objects.create(name='Test Mother')
        condition = State.objects.create(mother=mother, scheduled_date=date(2023, 12, 12),
                                         scheduled_time=time(10, 0))

        form = form_class(instance=condition)

        self.assertEqual(form.initial['scheduled_time'], time(10, 0))

    def test_form_add_current_obj_attr_exists(self):
        request = self.factory.get('/admin/mothers/condition/add/')
        self.condition_admin.get_form(request)

        self.assertIsNone(self.condition_admin.current_obj)

    def test_form_change_current_obj_attr_exists(self):
        request = self.factory.get('/admin/mothers/condition/123/change/')
        mother = Mother.objects.create(name='Test Mother')
        condition_instance = State.objects.create(mother=mother)
        self.condition_admin.get_form(request, obj=condition_instance)

        self.assertEqual(self.condition_admin.current_obj, condition_instance)
