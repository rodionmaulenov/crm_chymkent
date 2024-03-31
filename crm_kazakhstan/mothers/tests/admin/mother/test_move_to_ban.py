from django.test import TestCase, RequestFactory
from django.contrib.auth.models import Permission
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.db import models

from gmail_messages.services.manager_factory import ManagerFactory
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
        self.user = User.objects.create(username='username', password='password', is_staff=True,
                                        stage=Stage.StageChoices.PRIMARY)

    def prepare_request(self, request):
        self.session.process_request(request)
        self.message.process_request(request)

    def test_moved_to_ban_with_custom_perm(self):
        mother = Mother.objects.create(name='name')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Ban.objects.create(mother=mother, comment='comment')

        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type=self.admin, obj=mother)

        request = self.factory.get('/')
        request.user = self.user
        self.prepare_request(request)

        queryset = self.admin.get_queryset(request)
        self.assertEqual(len(queryset), 1)

        result = self.admin.move_to_ban(request, queryset)
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.url, f'/admin/mothers/ban/add/?mother={mother.pk}')

    def test_moved_to_ban_with_model_perm(self):
        mother = Mother.objects.create(name='name')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        Ban.objects.create(mother=mother, comment='comment')

        view_permission = Permission.objects.get(codename='view_mother')
        self.user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.user
        self.prepare_request(request)

        queryset = self.admin.get_queryset(request)
        self.assertEqual(len(queryset), 1)

        result = self.admin.move_to_ban(request, queryset)
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.url, f'/admin/mothers/ban/add/?mother={mother.pk}')
