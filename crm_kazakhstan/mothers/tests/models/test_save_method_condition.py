from guardian.shortcuts import get_perms

from django.contrib.auth.models import Group
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import models

from mothers.models import Condition, Mother

User = get_user_model()
Condition: models
Mother: models


class ConditionSaveMethodTest(TestCase):

    def test_condition_has_object_perms(self):
        primary_stage_group, _ = Group.objects.get_or_create(name='primary_stage')
        mother = Mother.objects.create(name='Mother 1')
        condition = Condition.objects.create(mother=mother)

        perms = get_perms(primary_stage_group, condition)
        self.assertIn('view_condition', perms)
        self.assertIn('change_condition', perms)
