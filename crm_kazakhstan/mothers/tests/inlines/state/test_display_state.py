from django.test import TestCase
from django.db import models
from django.contrib import admin

from mothers.inlines import StateInline
from mothers.models import Mother, State

Mother: models
State: models


class DisplayStateMethodTest(TestCase):

    def setUp(self):
        self.mother = Mother.objects.create(name="Test")
        self.inline_condition = StateInline(State, admin.site)

    def test_display_state(self):
        condition = State.objects.create(mother=self.mother, condition=State.ConditionChoices.NO_BABY)
        state_display = self.inline_condition.display_state(condition)

        expected_value = condition.get_condition_display()
        self.assertEqual(state_display, expected_value)

    def test_condition_display_state(self):
        condition = State.objects.create(mother=self.mother, condition=State.ConditionChoices.EMPTY)
        state_display = self.inline_condition.display_state(condition)

        expected_value = condition.get_condition_display()
        self.assertEqual(state_display, expected_value)
