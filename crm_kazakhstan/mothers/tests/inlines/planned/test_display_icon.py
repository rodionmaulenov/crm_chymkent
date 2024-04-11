from datetime import date, time

from django.test import TestCase
from django.contrib import admin
from django.db import models
from mothers.models import Mother, Planned
from mothers.inlines import PlannedInline

Mother: models
Planned: models


class DisplayIconTest(TestCase):
    def setUp(self):
        self.mother = Mother.objects.create(name="Test")
        self.inline = PlannedInline(Planned, admin.site)

    def test_finished_false(self):
        planned = Planned.objects.create(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            note='',
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(1, 0, 0),
            created=date.today(),
            finished=False)

        icon = self.inline.display_icon(planned)
        expected_value = ('<img src="/static/mothers/icons/red_check_mark.jpg" '
                          'alt="Failure" style="width: 18px; height: 20px;"/>')

        self.assertEqual(icon, expected_value)

    def test_finished_true(self):
        planned = Planned.objects.create(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            note='',
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(1, 0, 0),
            created=date.today(),
            finished=True)

        icon = self.inline.display_icon(planned)
        expected_value = ('<img src="/static/mothers/icons/green_check_mark.jpg" '
                          'alt="Success" style="width: 18px; height: 20px;"/>')
        self.assertEqual(icon, expected_value)

