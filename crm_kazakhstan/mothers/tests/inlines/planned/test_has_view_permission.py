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


class HasViewPermissionTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.mother = Mother.objects.create(name="Test")
        self.staff_user = User.objects.create_user(username='staff_user', password='password', is_staff=True,
                                                   timezone='Europe/Kyiv')
        self.superuser = User.objects.create_superuser(username='superuser', password='password')
        self.inline = PlannedInline(Planned, admin.site)

    def test_super_user_has_perm(self):
        planned = Planned.objects.create(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            note='',
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(1, 0, 0),
            created=date.today(),
            finished=False)

        request = self.factory.get('/')
        request.user = self.superuser

        result = self.inline.has_view_permission(request, planned)
        self.assertTrue(result)

    def test_staff_user_has_perm(self):
        planned = Planned.objects.create(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            note='',
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(1, 0, 0),
            created=date.today(),
            finished=False)

        request = self.factory.get('/')
        request.user = self.staff_user

        result = self.inline.has_view_permission(request, planned)
        self.assertTrue(result)

