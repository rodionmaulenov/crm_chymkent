from django.test import TestCase
from django.db import models
from django.contrib import admin

from mothers.inlines import ConditionInline
from mothers.models import Mother, Condition

Mother: models
Condition: models


class DisplayReasonMethodTest(TestCase):

    def setUp(self):
        self.mother = Mother.objects.create(name="Test")

        self.inline_condition = ConditionInline(Condition, admin.site)

    def test_display_reason_if_exists(self):
        condition = Condition.objects.create(mother=self.mother, condition=Condition.ConditionChoices.NO_BABY,
                                             reason='for example')
        reason_display = self.inline_condition.display_reason(condition)

        expected_value = condition.reason
        self.assertEqual(reason_display, expected_value)

    def test_without_reason(self):
        condition = Condition.objects.create(mother=self.mother, condition=Condition.ConditionChoices.NO_BABY)
        reason_display = self.inline_condition.display_reason(condition)

        expected_value = '_'
        self.assertEqual(reason_display, expected_value)

