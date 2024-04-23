from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models

from documents.admin import DocumentProxyAdmin
from documents.models import DocumentProxy
from mothers.models import Mother, Stage

User = get_user_model()
Stage: models
Mother: models


class AddDocumentTest(TestCase):
    def setUp(self):
        self.document_admin = DocumentProxyAdmin(DocumentProxy, admin.site)
        self.factory = RequestFactory()
        self.mother = Mother.objects.create(name='test')
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY, finished=False)

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True,
                                              stage=Stage.StageChoices.PRIMARY)

    def test_add_document_link(self):
        request = self.factory.get('/')
        request.user = self.superuser
        self.document_admin.request = request

        add_new = self.document_admin.add_document(self.mother)
        required = f'<a href="/admin/documents/document/add/?mother={self.mother.id}" ><b>add new</b></a>'
        self.assertEqual(add_new, required)
