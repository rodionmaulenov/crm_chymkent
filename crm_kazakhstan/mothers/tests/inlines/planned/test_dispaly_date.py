from datetime import date, time

from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.db import models
from django.contrib.auth import get_user_model
from mothers.models import Mother, Planned
from mothers.inlines import PlannedInline

User = get_user_model()
Mother: models
Planned: models


class DisplayDateTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.mother = Mother.objects.create(name="Test")
        self.staff_user = User.objects.create_user(username='staff_user', password='password', is_staff=True,
                                                   timezone='Europe/Kyiv')
        self.inline = PlannedInline(Planned, admin.site)

    def test_planned_date(self):
        planned = Planned.objects.create(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            note='',
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(1, 0, 0),
            created=date.today(),
            finished=False)

        request = self.factory.get('')
        request.user = self.staff_user

        self.inline.request = request

        d = self.inline.display_date(planned)
        self.assertEqual(d, '18.01.2024')


