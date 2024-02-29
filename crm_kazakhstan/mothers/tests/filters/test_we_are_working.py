from datetime import datetime, time

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.utils import timezone

from mothers.models import State, Mother, Stage
from mothers.admin import MotherAdmin
from mothers.filters import BoardFilter

MotherAdmin: admin.ModelAdmin
State: models
Mother: models
Stage: models

User = get_user_model()


class WeAreWorkingFilterTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')

        self.factory = RequestFactory()

        self.custom_filter = BoardFilter
        self.admin_site = AdminSite()
        self.mother_admin_instance = MotherAdmin(Mother, self.admin_site)

    def test_we_are_working(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        State.objects.create(
            mother=mother,
            condition=State.ConditionChoices.CREATED,
            finished=True
        )
        State.objects.create(
            mother=mother,
            condition=State.ConditionChoices.WORKING,
            finished=False
        )

        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = self.custom_filter(
            request, {'filter_set': 'already_working'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 1)

    def test_not_we_are_working(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        State.objects.create(
            mother=mother,
            condition=State.ConditionChoices.CREATED,
            finished=True
        )
        State.objects.create(
            mother=mother,
            condition=State.ConditionChoices.WORKING,
            finished=True
        )

        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = self.custom_filter(
            request, {'filter_set': 'already_working'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)
