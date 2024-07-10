from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib import admin

from documents.admin import DocumentProxyAdmin
from documents.models import Document

from mothers.models import Stage

User = get_user_model()
Stage: models
Mother: models


class GetListDisplayTest(TestCase):
    def setUp(self):
        self.document_admin = DocumentProxyAdmin(Document, admin.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True,
                                              stage=Stage.StageChoices.PRIMARY)

    def test_user_on_primary_stage(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        list_display = self.document_admin.get_list_display(request)
        expected = ('custom_name', 'add_main_docs')
        self.assertEqual(list_display, expected)

    def test_user_on_first_visit_stage(self):
        staff_first_visit = User.objects.create(username='staff_user2', password='password', is_staff=True,
                                                stage=Stage.StageChoices.FIRST_VISIT)
        request = self.factory.get('/')
        request.user = staff_first_visit
        list_display = self.document_admin.get_list_display(request)
        expected = ('custom_name', 'add_main_docs', 'add_additional_docs')
        self.assertEqual(list_display, expected)
