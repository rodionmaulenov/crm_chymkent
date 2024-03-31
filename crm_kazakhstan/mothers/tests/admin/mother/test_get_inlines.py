from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.db import models
from django.utils import timezone

from mothers.admin import MotherAdmin
from mothers.inlines import BanInline, StateInline
from mothers.models import Mother, Ban, State

Mother: models
Ban: models
State: models


class GetInlinesTest(TestCase):
    def setUp(self):
        self.admin = MotherAdmin(Mother, admin.site)
        self.factory = RequestFactory()
        self.mother = Mother.objects.create(name='test_name')

    def test_when_state_inline_equal_one(self):
        State.objects.create(mother=self.mother, scheduled_date=timezone.now().date(),
                             scheduled_time=timezone.now().time())
        request = self.factory.get('/')
        inlines = self.admin.get_inlines(request, self.mother)
        self.assertEqual(inlines, ())

    def test_when_state_inline_equal_one_and_ban(self):
        State.objects.create(mother=self.mother, scheduled_date=timezone.now().date(),
                             scheduled_time=timezone.now().time())
        Ban.objects.create(mother=self.mother, comment='comment')
        request = self.factory.get('/')
        inlines = self.admin.get_inlines(request, self.mother)
        self.assertIn(BanInline, inlines)

    def test_when_state_inline_equal_more_than_one_and_ban(self):
        State.objects.create(mother=self.mother, scheduled_date=timezone.now().date(),
                             scheduled_time=timezone.now().time())
        State.objects.create(mother=self.mother, scheduled_date=timezone.now().date(),
                             scheduled_time=timezone.now().time())
        Ban.objects.create(mother=self.mother, comment='comment')
        request = self.factory.get('/')
        inlines = self.admin.get_inlines(request, self.mother)
        self.assertIn(BanInline, inlines)
        self.assertIn(StateInline, inlines)

    def test_fully_empty(self):
        request = self.factory.get('/')
        inlines = self.admin.get_inlines(request, self.mother)
        self.assertEqual(inlines, ())
