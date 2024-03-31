from datetime import datetime, time, date

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.utils import timezone

from mothers.models import State, Mother, Stage, Planned
from mothers.admin import MotherAdmin
from mothers.filters import ActionFilter

MotherAdmin: admin.ModelAdmin
State: models
Mother: models
Planned: models
Stage: models

User = get_user_model()


class ActionFilterTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')

        self.factory = RequestFactory()

        self.custom_filter = ActionFilter
        self.admin_site = AdminSite()
        self.mother_admin_instance = MotherAdmin(Mother, self.admin_site)

    def test_state_exists(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        State.objects.create(
            mother=mother,
            condition=State.ConditionChoices.CREATED,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            finished=False
        )

        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = self.custom_filter(
            request, {'actions': 'state_actions'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 1)

    def test_state_not_exists(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        State.objects.create(
            mother=mother,
            condition=State.ConditionChoices.CREATED,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            finished=True
        )

        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = self.custom_filter(
            request, {'actions': 'state_actions'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)

    def test_plan_exists(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Planned.objects.create(mother=mother, finished=False, scheduled_date=date(2023, 12, 15),
                               scheduled_time=time(21, 20, 0))

        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = self.custom_filter(
            request, {'actions': 'planned_actions'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 1)

    def test_plan_not_exists(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Planned.objects.create(mother=mother, finished=True, scheduled_date=date(2023, 12, 15),
                               scheduled_time=time(21, 20, 0))

        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = self.custom_filter(
            request, {'actions': 'planned_actions'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)

