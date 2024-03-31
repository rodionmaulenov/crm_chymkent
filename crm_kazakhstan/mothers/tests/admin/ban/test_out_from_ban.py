from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.db import models

from gmail_messages.services.manager_factory import ManagerFactory

from mothers.admin import BanAdmin
from mothers.models import Mother, Stage, Ban

User = get_user_model()

Mother: models
Stage: models
Ban: models


class OutFromBanTest(TestCase):
    def setUp(self):
        self.admin = BanAdmin(Ban, admin.site)
        self.factory = RequestFactory()
        self.session = SessionMiddleware()
        self.message = MessageMiddleware()
        self.user = User.objects.create(username='username', password='password', is_staff=True,
                                        stage=Stage.StageChoices.PRIMARY)

    def prepare_request(self, request):
        self.session.process_request(request)
        self.message.process_request(request)

    def test_moved_out_ban(self):
        mother = Mother.objects.create(name='name')
        Stage.objects.create(mother=mother, stage=Stage.StageChoices.BAN, finished=False)
        ban = Ban.objects.create(mother=mother, comment='comment', banned=False)

        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type=self.admin, obj=ban)

        request = self.factory.get('/')
        request.user = self.user
        self.prepare_request(request)

        queryset = self.admin.get_queryset(request)
        self.assertEqual(len(queryset), 1)

        self.admin.out_from_ban(request, queryset)

        ban.refresh_from_db()

        queryset = self.admin.get_queryset(request)
        self.assertEqual(list(queryset), [])

        stage = mother.stage_set.last()
        stage.refresh_from_db()

        self.assertEqual(ban.banned, True)
        self.assertEqual(stage.stage, Stage.StageChoices.PRIMARY.value)