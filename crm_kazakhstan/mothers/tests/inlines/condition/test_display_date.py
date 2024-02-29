from datetime import date, time
from freezegun import freeze_time

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib import admin

from mothers.inlines import StateInline
from mothers.models import Mother, State

Mother: models
State: models

User = get_user_model()


class DisplayDateMethodTest(TestCase):

    def setUp(self):
        self.mother = Mother.objects.create(name="Test")
        self.staff_user = User.objects.create_user(username='staff_user', password='password', is_staff=True,
                                                   timezone='Europe/Kyiv')
        self.inline_condition = StateInline(State, admin.site)

    @freeze_time("2023-12-12 23:00:00")
    def test_display_date(self):
        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.staff_user
        self.inline_condition.request = request
        condition = State.objects.create(mother=self.mother, scheduled_date=date(2023, 12, 12),
                                             scheduled_time=time(23, 0, 0))

        date_display = self.inline_condition.display_date(condition)
        expected_value = '13 Dec 2023'

        self.assertEqual(date_display, expected_value)

    def test_without_date(self):
        condition = State.objects.create(mother=self.mother)
        date_display = self.inline_condition.display_date(condition)

        expected_value = '_'
        self.assertEqual(date_display, expected_value)
