from datetime import datetime, time
from freezegun import freeze_time

from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from mothers.models import Mother, Condition, Stage
from mothers.admin import MotherAdmin

User = get_user_model()

Mother: models
Condition: models
Stage: models


class GetOrderingMethodTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = MotherAdmin(Mother, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')

    @freeze_time("2023-12-12 21:00:00")
    def test_when_filtered_queryset_date_or_time(self):
        mother = Mother.objects.create(name='Test Mother')
        mother1 = Mother.objects.create(name='Test1 Mother')

        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother1, stage=Stage.StageChoices.PRIMARY)

        condition = Condition.objects.create(
            mother=mother,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            scheduled_time=time(20, 40, 0),
            condition=Condition.ConditionChoices.WROTE_IN_WHATSAPP_AND_WAITING,
            finished=False
        )
        condition.created = datetime(2023, 12, 11, tzinfo=timezone.utc)
        condition.save()

        condition1 = Condition.objects.create(
            mother=mother1,
            scheduled_date=datetime(2023, 12, 11, tzinfo=timezone.utc),
            scheduled_time=time(20, 40, 0),
            condition=Condition.ConditionChoices.NO_BABY,
            finished=False
        )
        condition1.created = datetime(2023, 12, 12, tzinfo=timezone.utc)
        condition1.save()

        request = self.factory.get('/mothers/mother?planned_time=datetime')
        request.user = self.superuser

        ordering = self.admin.get_ordering(request)
        self.assertEqual(['-condition__created'], ordering)

        queryset = self.admin.get_queryset(request).order_by('-condition__created')
        self.assertEqual(queryset.first(), mother1)

    def test_when_filtered_queryset_what_reason(self):
        mother = Mother.objects.create(name='Test Mother')
        mother1 = Mother.objects.create(name='Test1 Mother')

        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother1, stage=Stage.StageChoices.PRIMARY)

        Condition.objects.create(
            mother=mother,
            condition=Condition.ConditionChoices.__empty__,
            finished=False
        )
        Condition.objects.create(
            mother=mother1,
            condition=Condition.ConditionChoices.__empty__,
            finished=False
        )

        request = self.factory.get('/mothers/mother?empty_state=empty_condition')
        request.user = self.superuser

        ordering = self.admin.get_ordering(request)
        self.assertEqual(['-condition__created'], ordering)

        queryset = self.admin.get_queryset(request).order_by('-condition__created')
        self.assertEqual(queryset.first(), mother1)