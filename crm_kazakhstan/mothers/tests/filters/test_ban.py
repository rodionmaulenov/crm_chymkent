from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.db import models

from mothers.models import State, Mother, Stage, Ban
from mothers.admin import MotherAdmin
from mothers.filters import BanFilter

MotherAdmin: admin.ModelAdmin
State: models
Mother: models
Ban: models
Stage: models

User = get_user_model()


class BanFilterTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')

        self.factory = RequestFactory()

        self.custom_filter = BanFilter
        self.admin_site = AdminSite()
        self.mother_admin_instance = MotherAdmin(Mother, self.admin_site)

    def test_ban_exists(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Ban.objects.create(mother=mother, comment='some comments', banned=False)
        State.objects.create(
            mother=mother,
            condition=State.ConditionChoices.CREATED,
            finished=True
        )

        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = self.custom_filter(
            request, {'ban': 'ban_exist'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 1)

    def test_ban_not_exists(self):
        mother = Mother.objects.create(name='Test Mother')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Ban.objects.create(mother=mother, comment='some comments', banned=True)
        State.objects.create(
            mother=mother,
            condition=State.ConditionChoices.CREATED,
            finished=True
        )

        request = self.factory.get('/')
        request.user = self.superuser

        filter_instance = self.custom_filter(
            request, {'ban': 'ban_exist'}, Mother, self.mother_admin_instance
        )
        queryset = filter_instance.queryset(request, self.mother_admin_instance.get_queryset(request))

        self.assertEqual(len(queryset), 0)