from datetime import datetime, time

from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.db import models
from django.utils import timezone

from mothers.models import Mother, Stage, Planned
from first_visit.admin import PrimaryVisitAdmin

Mother: models
Stage: models
Planned: models


class AdminDisplayFirstPlannedVisitTest(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

        self.first_visit_admin = PrimaryVisitAdmin(Mother, admin.site)

        self.mother = Mother.objects.create(name='Test Mother')

        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY)

        self.planned = Planned.objects.create(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            scheduled_date=datetime(2023, 12, 27, tzinfo=timezone.utc),
            scheduled_time=time(21, 20, 0)
        )

    def test_ok_first_planned_visit(self):
        analyzes_in_shymkent = self.first_visit_admin.first_planned_visit(self.mother)

        self.assertEqual(analyzes_in_shymkent, self.planned)


class AdminDisplayFirstPlannedDateVisitTest(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

        self.first_visit_admin = PrimaryVisitAdmin(Mother, admin.site)

        self.mother = Mother.objects.create(name='Test Mother')

        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY)

        self.planned = Planned.objects.create(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            scheduled_date=datetime(2023, 12, 27, tzinfo=timezone.utc),
            scheduled_time=time(21, 20, 0)
        )

    def test_ok_first_planned_visit(self):
        analyzes_in_shymkent_date = self.first_visit_admin.first_planned_visit_date(self.mother)

        self.assertEqual(analyzes_in_shymkent_date, self.planned.scheduled_date.date())
