from guardian.shortcuts import assign_perm

from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models

from mothers.models import Mother, Stage, Ban
from mothers.admin import BanAdmin

User = get_user_model()
Stage: models
Mother: models
Ban: models


class GetQuerySetTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = BanAdmin(Ban, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True)

    def test_queryset_for_superuser(self):
        request = self.factory.get('/')
        request.user = self.superuser
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.BAN, finished=False)
        Ban.objects.create(mother=mother, comment='some comment', banned=False)

        self.assertEqual(len(queryset), 1)

    def test_queryset_for_staff_user_with_model_lvl_perm(self):
        view_permission = Permission.objects.get(codename='view_ban')
        self.staff_user.user_permissions.add(view_permission)
        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        mother = Mother.objects.create(name='Mother 1')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.BAN, finished=False)
        Ban.objects.create(mother=mother, comment='some comment', banned=False)

        self.assertEqual(len(queryset), 1)

    def test_queryset_for_staff_user(self):
        mother = Mother.objects.create(name='Mother 1')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.BAN, finished=False)
        ban = Ban.objects.create(mother=mother, comment='some comment', banned=False)
        assign_perm('ban_state', self.staff_user, ban)

        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        self.assertEqual(len(queryset), 1)

    def test_two_different_user_have_various_instance(self):
        # first user
        mother = Mother.objects.create(name='Mother 1')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.BAN, finished=False)
        ban = Ban.objects.create(mother=mother, comment='some comment', banned=False)
        assign_perm('ban_state', self.staff_user, ban)

        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        self.assertEqual(len(queryset), 1)

        # second user
        second_user = User.objects.create(username='second_user', password='password', is_staff=True)

        mother = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.BAN, finished=False)
        ban = Ban.objects.create(mother=mother, comment='some comment', banned=False)
        assign_perm('ban_state', second_user, ban)

        mother = Mother.objects.create(name='Mother 2.1')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.BAN, finished=False)
        ban = Ban.objects.create(mother=mother, comment='some comment', banned=False)
        assign_perm('ban_state', second_user, ban)

        request = self.factory.get('/')
        request.user = second_user
        queryset = self.admin.get_queryset(request)

        self.assertEqual(len(queryset), 2)

        # third user
        third_user = User.objects.create(username='third_user', password='password', is_staff=True)

        view_permission = Permission.objects.get(codename='view_ban')
        third_user.user_permissions.add(view_permission)

        mother = Mother.objects.create(name='Mother 3')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.BAN, finished=False)
        Ban.objects.create(mother=mother, comment='some comment', banned=False)

        request = self.factory.get('/')
        request.user = third_user
        queryset = self.admin.get_queryset(request)

        self.assertEqual(len(queryset), 4)

    def test_not_queryset_for_staff_user(self):
        mother = Mother.objects.create(name='Mother 1')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.BAN, finished=False)
        Ban.objects.create(mother=mother, comment='some comment', banned=False)

        request = self.factory.get('/')
        request.user = self.staff_user
        queryset = self.admin.get_queryset(request)

        self.assertEqual(len(queryset), 0)
