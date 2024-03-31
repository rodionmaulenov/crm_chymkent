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


class StateDateTimeTest(TestCase):

    def setUp(self):
        self.mother = Mother.objects.create(name='Test')
        self.factory = RequestFactory()
        self.admin = MotherAdmin(Mother, AdminSite())
        self.superuser = User.objects.create_superuser(username='superuser', password='password')

    def test_state_finished(self):
        State.objects.create(mother=self.mother, finished=True, scheduled_date=date(2023, 12, 13),
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

        result = self.admin.state_datetime(mother=self.mother)

        self.assertIsNone(result)

    def test_state_not_finished(self):
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

        result = self.admin.state_datetime(mother=self.mother)
        self.assertEqual(result, '<strong>12 December 23/18:20</strong>')
