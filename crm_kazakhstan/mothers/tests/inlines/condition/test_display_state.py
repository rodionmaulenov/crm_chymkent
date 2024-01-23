from django.test import TestCase
from django.db import models
from django.contrib import admin

from mothers.inlines import ConditionInline
from mothers.models import Mother, Condition

Mother: models
Condition: models


class DisplayStateMethodTest(TestCase):

    def setUp(self):
        mother = Mother.objects.create(name="Test")
        self.condition = Condition.objects.create(mother=mother, condition=Condition.ConditionChoices.NO_BABY)
        self.inline_condition = ConditionInline(Condition, admin.site)

    def test_display_state(self):
        state_display = self.inline_condition.display_state(self.condition)

        expected_value = self.condition.get_condition_display()
        self.assertEqual(state_display, expected_value)
