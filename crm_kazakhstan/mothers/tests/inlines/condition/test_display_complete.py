from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib import admin

from mothers.inlines import StateInline
from mothers.models import Mother, State

Mother: models
State: models

User = get_user_model()


class DisplayCompleteMethodTest(TestCase):

    def setUp(self):
        self.mother = Mother.objects.create(name="Test")
        self.staff_user = User.objects.create_user(username='staff_user', password='password', is_staff=True,
                                                   timezone='Europe/Kyiv')
        self.inline_condition = StateInline(State, admin.site)

    def test_finished_false(self):
        condition = State.objects.create(mother=self.mother, finished=False)

        not_complete = self.inline_condition.display_complete(condition)

        expected_value = ('<img src="/static/mothers/icons/red_check_mark.jpg" '
                          'alt="Failure" style="width: 18px; height: 20px;"/>')

        self.assertEqual(not_complete, expected_value)

    def test_finished_True(self):
        condition = State.objects.create(mother=self.mother, finished=True)
        complete = self.inline_condition.display_complete(condition)

        expected_value = ('<img src="/static/mothers/icons/green_check_mark.jpg" '
                          'alt="Success" style="width: 18px; height: 20px;"/>')
        self.assertEqual(complete, expected_value)
