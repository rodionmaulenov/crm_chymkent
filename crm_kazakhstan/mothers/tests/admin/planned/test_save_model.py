from datetime import date, time
from freezegun import freeze_time
from guardian.shortcuts import get_perms
from urllib.parse import urlencode

from django.db import models
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.urls import reverse

from mothers.models import Planned, Mother, Stage
from mothers.admin import PlannedAdmin

User = get_user_model()

Mother: models


class SaveModelTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = PlannedAdmin(Planned, self.site)
        self.factory = RequestFactory()
        self.mother = Mother.objects.create(name='Mother')

        self.user_timezone = User.objects.create_superuser(username='staff_user', password='password',
                                                           timezone='Europe/Kyiv', is_staff=True,
                                                           stage=Stage.StageChoices.PRIMARY)

    @freeze_time("2024-04-18 12:00:00")
    def test_convert_local_time_to_utc(self):

        existing_planned = Planned(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            note='',
            scheduled_date=date(2023, 1, 18),
            scheduled_time=time(1, 0, 0),
            created=date(2023, 1, 17),
            finished=False)

        form_data = {
            'mother': self.mother.pk,
            'plan': Planned.PlannedChoices.FIRST_TEST,
            'note': '',
            'scheduled_date': date(2024, 1, 18),
            'scheduled_time': time(1, 0, 0),
            'created': date.today(),
            'finished': False
        }

        relative_path = reverse('admin:mothers_state_change', args=[existing_planned.pk])
        query_params = {'mother': self.mother.pk, '_changelist_filters': '/admin/mothers/mother/'}
        url = f"{relative_path}?{urlencode(query_params)}"

        request = self.factory.get(url)
        request.user = self.user_timezone

        form_class = self.admin.get_form(request=request, change=False)

        form_instance = form_class(data=form_data, instance=None)

        if form_instance.is_valid():
            obj = form_instance.save(commit=False)
            self.admin.save_model(request=request, obj=obj, form=form_instance, change=False)

            obj.refresh_from_db()
            self.assertIsNotNone(obj.pk)

            self.assertEqual(obj.scheduled_date, date(2024, 1, 17))
            self.assertEqual(obj.scheduled_time, time(23, 0, 0))

        else:
            self.fail(f'Form is not valid: {form_instance.errors}')

    def test_assigned_custom_perm(self):
        obj = Planned(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            note='',
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(1, 0, 0),
            created=date.today(),
            finished=False)

        self.assertIsNone(obj.pk)

        request = self.factory.get('/')
        request.user = self.user_timezone

        form = self.admin.get_form(request)
        self.admin.save_model(request, obj, form, change=False)

        obj.refresh_from_db()
        self.assertIsNotNone(obj.pk)

        perms = get_perms(self.user_timezone, obj)
        self.assertIn('primary_planned_staff_user', perms)
