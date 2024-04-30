from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.db import models
from django.urls import reverse

from ban.admin import BanProxyAdmin
from ban.models import BanProxy

from gmail_messages.services.manager_factory import ManagerFactory

from mothers.admin import MotherAdmin
from mothers.models import Mother, Stage

from ban.models import Ban

User = get_user_model()

Mother: models
Stage: models
Ban: models


class OutFromBanTest(TestCase):
    def setUp(self):
        self.admin_ban_proxy = BanProxyAdmin(BanProxy, admin.site)
        self.admin_mother = MotherAdmin(Mother, admin.site)
        self.factory = RequestFactory()
        self.session = SessionMiddleware()
        self.message = MessageMiddleware()
        self.user = User.objects.create(username='username', password='password', is_staff=True,
                                        stage=Stage.StageChoices.PRIMARY)

        self.mother = Mother.objects.create(name='name')
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.BAN, finished=False)
        Ban.objects.create(mother=self.mother, comment='comment', banned=True)

    def prepare_request(self, request):
        self.session.process_request(request)
        self.message.process_request(request)

    def test_moved_out_ban(self):
        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type=self.admin_mother, obj=self.mother)

        request = self.factory.get('/')
        request.user = self.user
        self.prepare_request(request)

        queryset_mother = self.admin_mother.get_queryset(request)
        self.assertEqual(list(queryset_mother), [])
        queryset = self.admin_ban_proxy.get_queryset(request)
        self.assertEqual(len(queryset), 1)

        self.admin_ban_proxy.out_from_ban(request, queryset)

        queryset_mother = self.admin_mother.get_queryset(request)
        self.assertEqual(len(queryset_mother), 1)
        queryset = self.admin_ban_proxy.get_queryset(request)
        self.assertEqual(len(queryset), 0)

        stage = self.mother.stage_set.last()
        self.assertEqual(stage.stage, Stage.StageChoices.PRIMARY.value)

    def test_redirect_on_change_list(self):
        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type=self.admin_mother, obj=self.mother)

        request = self.factory.get('/')
        request.user = self.user
        self.prepare_request(request)

        queryset = self.admin_ban_proxy.get_queryset(request)
        result = self.admin_ban_proxy.out_from_ban(request, queryset)

        mother_changelist = reverse('admin:mothers_mother_changelist')
        self.assertEqual(result.url, mother_changelist)
        self.assertEqual(result.status_code, 302)
