from datetime import datetime, time

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.utils import timezone

from mothers.models import State, Mother, Stage
from mothers.admin import MotherAdmin
from mothers.filters import BoardFilter

MotherAdmin: admin.ModelAdmin
State: models
Mother: models
Stage: models

User = get_user_model()


class AssignNewStatusFilterTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')

        self.factory = RequestFactory()

        self.custom_filter = BoardFilter
        self.admin_site = AdminSite()
        self.mother_admin_instance = MotherAdmin(Mother, self.admin_site)

    def test_not_planned(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        State.objects.create(
            mother=mother,
            condition=State.ConditionChoices.CREATED,
            finished=True
        )

        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = self.custom_filter(
            request, {'filter_set': 'assign_new_state'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)

    def test_not_planned_2(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        State.objects.create(
            mother=mother,
            condition=State.ConditionChoices.CREATED,
            finished=True
        )
        State.objects.create(
            mother=mother,
            reason='Some reason',
            condition=State.ConditionChoices.EMPTY,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            finished=False
        )
        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = self.custom_filter(
            request, {'filter_set': 'assign_new_state'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)

    def test_planned(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        State.objects.create(
            mother=mother,
            condition=State.ConditionChoices.CREATED,
            finished=True
        )
        State.objects.create(
            mother=mother,
            reason='Some reason',
            condition=State.ConditionChoices.EMPTY,
            scheduled_date=datetime(2023, 12, 12, tzinfo=timezone.utc),
            scheduled_time=time(14, 30, 0),
            finished=True
        )

        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = self.custom_filter(
            request, {'filter_set': 'assign_new_state'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 1)