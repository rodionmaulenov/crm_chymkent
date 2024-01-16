from guardian.shortcuts import assign_perm

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
        self.rushana = User.objects.create_user(username='Rushana', password='password')

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

    def test_has_not_access_to_first_layer_site_mother_rushana(self):
        request = self.factory.get('/')
        request.user = self.rushana
        access = self.admin.has_module_permission(request)

        self.assertFalse(access)

    def test_has_not_staff_user_access_to_first_layer_site_mother(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        access = self.admin.has_module_permission(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY)

        self.assertFalse(access)

    def test_rushana_has_not_access_to_first_layer_site_mother(self):
        request = self.factory.get('/')
        request.user = self.rushana
        access = self.admin.has_module_permission(request)

        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY)

        self.assertFalse(access)

    def test_and_not_has_access_to_first_layer_site_mother_rushana_and_mothers_on_FV_stage(self):
        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.FIRST_VISIT)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.FIRST_VISIT)

        assign_perm('view_mother', self.rushana, mother)
        assign_perm('change_mother', self.rushana, mother)

        assign_perm('view_mother', self.rushana, mother2)
        assign_perm('change_mother', self.rushana, mother2)

        request = self.factory.get('/')
        request.user = self.rushana
        access = self.admin.has_module_permission(request)

        self.assertFalse(access)

    def test_and_has_access_to_first_layer_site_mother_rushana_mothers_on_FV_and_PRIMARY(self):
        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.FIRST_VISIT)

        assign_perm('view_mother', self.rushana, mother)
        assign_perm('change_mother', self.rushana, mother)

        assign_perm('view_mother', self.rushana, mother2)
        assign_perm('change_mother', self.rushana, mother2)

        request = self.factory.get('/')
        request.user = self.rushana
        access = self.admin.has_module_permission(request)

        self.assertTrue(access)

    def test_has_access_to_first_layer_site_mother_rushana_mothers_on_primary(self):
        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY)

        assign_perm('view_mother', self.rushana, mother)
        assign_perm('change_mother', self.rushana, mother)

        assign_perm('view_mother', self.rushana, mother2)
        assign_perm('change_mother', self.rushana, mother2)

        request = self.factory.get('/')
        request.user = self.rushana
        access = self.admin.has_module_permission(request)

        self.assertTrue(access)

    def test_has_access_to_first_layer_site_mother_rushana_mother_on_primary_stage(self):
        mother = Mother.objects.create(name='Mother 1')
        mother2 = Mother.objects.create(name='Mother 2')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY)
        Stage.objects.create(mother=mother2, stage=Stage.StageChoices.PRIMARY)

        assign_perm('view_mother', self.rushana, mother)
        assign_perm('change_mother', self.rushana, mother)

        request = self.factory.get('/')
        request.user = self.rushana
        access = self.admin.has_module_permission(request)

        self.assertTrue(access)
