from datetime import date, time

from django.test import TestCase
from django.contrib import admin
from django.db import models

from mothers.models import Mother, Planned
from mothers.inlines import PlannedInline

Mother: models
Planned: models


class DisplayPlanTest(TestCase):
    def setUp(self):
        self.mother = Mother.objects.create(name="Test")
        self.inline = PlannedInline(Planned, admin.site)

    def test_upper_bold_text_of_plan_(self):
        planned = Planned.objects.create(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            note='',
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(1, 0, 0),
            created=date.today(),
            finished=False)

        text = self.inline.display_plan(planned)
        example = 'laboratory'.upper()
        self.assertEqual(text, f'<strong>{example}</strong>')
