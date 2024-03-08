from guardian.shortcuts import assign_perm

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import Permission
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.db import models

from mothers.admin import MotherAdmin
from mothers.models import Mother, Stage, Ban

User = get_user_model()

Mother: models
Stage: models
Ban: models


class MoveToBanTest(TestCase):
    def setUp(self):
        self.admin = MotherAdmin(Mother, admin.site)
        self.factory = RequestFactory()
        self.session = SessionMiddleware()
        self.message = MessageMiddleware()
        self.user = User.objects.create(username='username', password='password', is_staff=True)

    def prepare_request(self, request):
        self.session.process_request(request)
        self.message.process_request(request)

    def test_moved_to_ban_with_custom_perm(self):
        mother = Mother.objects.create(name='name')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Ban.objects.create(mother=mother, comment='comment')
        assign_perm('primary_stage', self.user, mother)

        mother_1 = Mother.objects.create(name='name1')
        Stage.objects.create(mother=mother_1, stage=Stage.StageChoices.PRIMARY, finished=False)
        Ban.objects.create(mother=mother_1, comment='comment')
        assign_perm('primary_stage', self.user, mother_1)

        request = self.factory.get('/')
        request.user = self.user
        self.prepare_request(request)

        queryset = self.admin.get_queryset(request)
        self.assertEqual(len(queryset), 2)

        self.admin.move_to_ban(request, queryset)

        queryset = self.admin.get_queryset(request)
        self.assertEqual(list(queryset), [])

        stage = mother.stage_set.last()
        stage_1 = mother_1.stage_set.last()

        self.assertEqual(stage.stage, Stage.StageChoices.BAN.value)
        self.assertEqual(stage_1.stage, Stage.StageChoices.BAN.value)

    def test_moved_to_ban_with_model_perm(self):
        mother = Mother.objects.create(name='name')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Ban.objects.create(mother=mother, comment='comment')
        view_permission = Permission.objects.get(codename='view_mother')
        self.user.user_permissions.add(view_permission)

        mother_1 = Mother.objects.create(name='name1')
        Stage.objects.create(mother=mother_1, stage=Stage.StageChoices.PRIMARY, finished=False)
        Ban.objects.create(mother=mother_1, comment='comment')
        view_permission = Permission.objects.get(codename='view_mother')
        self.user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.user
        self.prepare_request(request)

        queryset = self.admin.get_queryset(request)
        self.assertEqual(len(queryset), 2)

        self.admin.move_to_ban(request, queryset)

        queryset = self.admin.get_queryset(request)
        self.assertEqual(list(queryset), [])

        stage = mother.stage_set.last()
        stage_1 = mother_1.stage_set.last()

        self.assertEqual(stage.stage, Stage.StageChoices.BAN.value)
        self.assertEqual(stage_1.stage, Stage.StageChoices.BAN.value)
