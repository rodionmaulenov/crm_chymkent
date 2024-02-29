from datetime import time, date
from freezegun import freeze_time

from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.db import models

from mothers.models import Mother, State
from mothers.admin import MotherAdmin
from mothers.services.state import filters_datetime, filtered_mothers

Mother: models
State: models

User = get_user_model()


class CreateConditionLinkTest(TestCase):

    def setUp(self):
        self.mother = Mother.objects.create(name='Test')
        self.factory = RequestFactory()
        self.admin = MotherAdmin(Mother, AdminSite())
        self.superuser = User.objects.create_superuser(username='superuser', password='password')

    @freeze_time("2023-12-12 22:00:00")
    def test_on_change_list_page_and_planned_time_has_not_come(self):
        State.objects.create(mother=self.mother, finished=False, scheduled_date=date(2023, 12, 13),
                             scheduled_time=time(21, 20, 0), reason='some reason')

        filters = filters_datetime(self.mother)
        on_filtered_page = filtered_mothers(filters)

        self.assertFalse(on_filtered_page)

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        result = self.admin.create_condition_datetime(obj=self.mother)

        self.assertEqual(result, 'Dec. 13, 2023, 21:20')

    @freeze_time("2023-12-12 22:00:00")
    def test_on_changelist_page_and_planned_time_has_come(self):
        State.objects.create(mother=self.mother, finished=False, scheduled_date=date(2023, 12, 12),
                             scheduled_time=time(18, 20, 0), reason='some reason')

        filters = filters_datetime(self.mother)
        on_filtered_page = filtered_mothers(filters)

        self.assertTrue(on_filtered_page)

        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        result = self.admin.create_condition_datetime(obj=self.mother)

        self.assertEqual(result, 'Dec. 12, 2023, 18:20')

    @freeze_time("2023-12-12 22:00:00")
    def test_on_filtered_changelist_page(self):
        State.objects.create(mother=self.mother, finished=False, scheduled_date=date(2023, 12, 12),
                             scheduled_time=time(18, 20, 0), reason='some reason')

        filters = filters_datetime(self.mother)
        on_filtered_page = filtered_mothers(filters)

        self.assertTrue(on_filtered_page)

        request = self.factory.get('admin/mothers/mother/?planned_time=datetime')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = self.superuser
        self.admin.request = request

        self.assertTrue(request.GET.get('planned_time'), 'datetime')

        result = self.admin.create_condition_datetime(obj=self.mother)

        self.assertEqual(result, 'Dec. 12, 2023, 18:20')
