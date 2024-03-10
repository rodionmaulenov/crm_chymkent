from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.db import models

from mothers.admin import MotherAdmin
from mothers.models import Mother, Stage, Ban

Mother: models
Ban: models


class GetActionsTest(TestCase):
    def setUp(self):
        self.admin = MotherAdmin(Mother, admin.site)
        self.factory = RequestFactory()

    def test_action_dict_without_move_to_ban(self):
        mother = Mother.objects.create(name='test')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.BAN, finished=False)
        Ban.objects.create(mother=mother, comment='some', banned=False)

        request = self.factory.get('/')
        action_dict = self.admin.get_actions(request)
        with self.assertRaises(KeyError):
            action = action_dict['move_to_ban']

    def test_action_dict_with_move_to_ban(self):
        mother = Mother.objects.create(name='test')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Ban.objects.create(mother=mother, comment='some', banned=False)

        request = self.factory.get('/')
        action_dict = self.admin.get_actions(request)
        self.assertTrue(action_dict['move_to_ban'])
