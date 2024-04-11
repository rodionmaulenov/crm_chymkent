from django.test import TestCase
from django.db import models
from django.contrib import admin
from django.utils import timezone

from mothers.inlines import StateInline
from mothers.models import Mother, State

Mother: models
State: models


class DisplayReasonMethodTest(TestCase):

    def setUp(self):
        self.mother = Mother.objects.create(name="Test")

        self.inline_condition = StateInline(State, admin.site)

    def test_display_reason_if_exists(self):
        condition = State.objects.create(mother=self.mother, condition=State.ConditionChoices.NO_BABY,
                                         reason='for example', scheduled_date=timezone.now().date(),
                                         scheduled_time=timezone.now().time())
        reason_display = self.inline_condition.display_reason(condition)

        expected_value = condition.reason
        self.assertEqual(reason_display, expected_value)

    def test_without_reason(self):
        condition = State.objects.create(mother=self.mother, condition=State.ConditionChoices.NO_BABY,
                                         scheduled_date=timezone.now().date(),
                                         scheduled_time=timezone.now().time())
        reason_display = self.inline_condition.display_reason(condition)

        expected_value = ''
        self.assertEqual(reason_display, expected_value)
