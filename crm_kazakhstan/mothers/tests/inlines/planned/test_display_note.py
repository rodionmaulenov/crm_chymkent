from datetime import date, time

from django.test import TestCase
from django.contrib import admin
from django.db import models
from mothers.models import Mother, Planned
from mothers.inlines import PlannedInline

Mother: models
Planned: models


class DisplayNoteTest(TestCase):
    def setUp(self):
        self.mother = Mother.objects.create(name="Test")
        self.inline = PlannedInline(Planned, admin.site)

    def test_empty_string(self):
        planned = Planned.objects.create(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            note='',
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(1, 0, 0),
            created=date.today(),
            finished=False)

        text = self.inline.display_note(planned)
        self.assertEqual(text, '')

    def test_some_note(self):
        planned = Planned.objects.create(
            mother=self.mother,
            plan=Planned.PlannedChoices.FIRST_TEST,
            note='some note',
            scheduled_date=date(2024, 1, 18),
            scheduled_time=time(1, 0, 0),
            created=date.today(),
            finished=False)

        text = self.inline.display_note(planned)
        self.assertEqual(text, 'some note')
