from django.contrib.auth.models import Group
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models
from guardian.shortcuts import assign_perm

from mothers.models import Mother, Stage
from mothers.admin import MotherAdmin

User = get_user_model()
Mother: models
Stage: models


class HasViePermissionMethodTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = MotherAdmin(Mother, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staffuser', password='password', is_staff=True)

        self.primary_stage_group, created = Group.objects.get_or_create(name='primary_stage')

    def test_super_user_has_view_perm(self):
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_change_permission(request)

        self.assertTrue(view)

    def test_super_user_has_view_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_change_permission(request, mother)

        self.assertTrue(view)

    def test_staff_user_has_not_view_perm(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_change_permission(request)

        self.assertFalse(view)

    def test_staff_user_has_not_view_perm_when_mother_not_on_PRIMARY_stage(self):
        self.staff_user.groups.add(self.primary_stage_group)
        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.FIRST_VISIT)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.FIRST_VISIT)

        assign_perm('view_mother', self.primary_stage_group, mother)
        assign_perm('change_mother', self.primary_stage_group, mother)

        assign_perm('view_mother', self.primary_stage_group, mother2)
        assign_perm('change_mother', self.primary_stage_group, mother2)

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_change_permission(request)

        self.assertFalse(view)

    def test_staff_user_has_view_perm(self):
        self.staff_user.groups.add(self.primary_stage_group)
        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY)

        assign_perm('view_mother', self.primary_stage_group, mother)
        assign_perm('change_mother', self.primary_stage_group, mother)

        assign_perm('view_mother', self.primary_stage_group, mother2)
        assign_perm('change_mother', self.primary_stage_group, mother2)

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_change_permission(request)

        self.assertTrue(view)

    def test_staff_user_has_view_perm_when_mother_on_different_stages(self):
        self.staff_user.groups.add(self.primary_stage_group)
        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.FIRST_VISIT)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY)

        assign_perm('view_mother', self.primary_stage_group, mother)
        assign_perm('change_mother', self.primary_stage_group, mother)

        assign_perm('view_mother', self.primary_stage_group, mother2)
        assign_perm('change_mother', self.primary_stage_group, mother2)

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_change_permission(request)

        self.assertTrue(view)

    def test_staff_user_has_not_view_perm_on_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_change_permission(request, mother)

        self.assertFalse(view)

    def test_staff_user_has_not_view_perm_on_obj_when_obj_without_obj_lvl_perms(self):
        self.staff_user.groups.add(self.primary_stage_group)
        mother = Mother.objects.create(name='Mother 1')

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_change_permission(request, mother)

        self.assertFalse(view)

    def test_staff_user_has_view_perm_on_obj(self):
        self.staff_user.groups.add(self.primary_stage_group)
        mother = Mother.objects.create(name='Mother 1')
        assign_perm('view_mother', self.primary_stage_group, mother)
        assign_perm('change_mother', self.primary_stage_group, mother)
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_change_permission(request, mother)

        self.assertTrue(view)

