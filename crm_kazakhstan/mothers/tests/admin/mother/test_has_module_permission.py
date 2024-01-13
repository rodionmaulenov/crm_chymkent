from guardian.shortcuts import assign_perm

from django.contrib.auth.models import Group
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models

from mothers.models import Mother, Stage
from mothers.admin import MotherAdmin

User = get_user_model()
Stage: models
Mother: models


class HasModulePermissionMethodTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = MotherAdmin(Mother, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staffuser', password='password', is_staff=True)

        # Create a group
        self.primary_stage_group, created = Group.objects.get_or_create(name='primary_stage')

    def test_has_access_to_first_layer_site_mother_for_superuser(self):
        request = self.factory.get('/')
        request.user = self.superuser
        access = self.admin.has_module_permission(request)

        self.assertTrue(access)

    def test_has_not_access_to_first_layer_site_mother_staff_user(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        access = self.admin.has_module_permission(request)

        self.assertFalse(access)

    def test_has_not_access_to_first_layer_site_mother_staff_user_with_group(self):
        self.staff_user.groups.add(self.primary_stage_group)
        request = self.factory.get('/')
        request.user = self.staff_user
        access = self.admin.has_module_permission(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY)

        self.assertFalse(access)

    def test_and_not_has_access_to_first_layer_site_mother_staff_user_with_group_and_mothers_obj_lvl_perms_on_FV(self):
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
        access = self.admin.has_module_permission(request)

        self.assertFalse(access)

    def test_and_has_access_to_first_layer_site_mother_staff_user_with_group_and_mothers_obj_lvl_perms_on_FV_and_PRIMARY(
            self):
        self.staff_user.groups.add(self.primary_stage_group)
        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.FIRST_VISIT)

        assign_perm('view_mother', self.primary_stage_group, mother)
        assign_perm('change_mother', self.primary_stage_group, mother)

        assign_perm('view_mother', self.primary_stage_group, mother2)
        assign_perm('change_mother', self.primary_stage_group, mother2)

        request = self.factory.get('/')
        request.user = self.staff_user
        access = self.admin.has_module_permission(request)

        self.assertTrue(access)

    def test_has_access_to_first_layer_site_mother_staff_user_with_group_and_mothers_obj_lvl_perms(self):
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
        access = self.admin.has_module_permission(request)

        self.assertTrue(access)

    def test_has_access_to_first_layer_site_mother_staff_user_with_group_and_mother_obj_lvl_perms(self):
        self.staff_user.groups.add(self.primary_stage_group)
        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY)

        assign_perm('view_mother', self.primary_stage_group, mother)
        assign_perm('change_mother', self.primary_stage_group, mother)

        request = self.factory.get('/')
        request.user = self.staff_user
        access = self.admin.has_module_permission(request)

        self.assertTrue(access)
