from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.db import models
from django.test import TestCase, RequestFactory

from mothers.admin import BanAdmin, MotherAdmin
from mothers.models import Ban, Mother, Stage

Mother: models
Ban: models
User = get_user_model()


class ResponseAddTest(TestCase):
    def setUp(self):
        self.mother = Mother.objects.create(name='test_mother')
        self.stage = Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        self.admin = BanAdmin(Ban, admin.site)
        self.mother_admin = MotherAdmin(Mother, admin.site)
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser(username='superuser', password='password')

        self.sm = SessionMiddleware()
        self.mm = MessageMiddleware()

    def prepare_request(self, request):
        self.sm.process_request(request)
        self.mm.process_request(request)

    def test_redirect_after_add(self):
        ban = Ban.objects.create(mother=self.mother, comment='test_comment', banned=False)

        request = self.factory.get('/')
        request.user = self.user
        self.prepare_request(request)

        queryset = self.mother_admin.get_queryset(request)
        self.assertEqual(len(queryset), 1)

        old_stage_mother = ban.mother.stage_set.filter(finished=False).first().stage
        self.assertEqual(old_stage_mother, Stage.StageChoices.PRIMARY)

        redirect = self.admin.response_add(request, ban)

        queryset = self.mother_admin.get_queryset(request)
        self.assertEqual(len(queryset), 0)

        new_stage_mother = ban.mother.stage_set.filter(finished=False).first().stage
        self.assertEqual(new_stage_mother, Stage.StageChoices.BAN)

        self.assertEqual(redirect.url, "/admin/mothers/mother/")
        self.assertEqual(redirect.status_code, 302)
