from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import Permission

from documents.admin import DocumentProxyAdmin
from documents.models import Document, MainDocument
from mothers.models import Mother, Stage

User = get_user_model()
Stage: models
Mother: models
MainDocument: models


class AddMainDocsTest(TestCase):
    def setUp(self):
        self.document_admin = DocumentProxyAdmin(Document, admin.site)
        self.factory = RequestFactory()
        self.mother = Mother.objects.create(name='test')
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY, finished=False)

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')

    def test_add_document_link(self):
        request = self.factory.get('/')
        request.user = self.superuser
        self.document_admin.request = request

        add_new = self.document_admin.add_main_docs(self.mother)
        mother_pk = self.mother.pk
        required = (
            f'<a class="add-change-link " href="/admin/documents/document/{mother_pk}/change/?mother={mother_pk}&amp;documents=main">'
        )
        self.assertIn(required, add_new)

    def test_if_user_has_only_view_perm(self):
        staff_user = User.objects.create(username='staff_user', password='password', is_staff=True)
        view_permission = Permission.objects.get(codename='view_document')
        staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = staff_user
        self.document_admin.request = request

        add_new = self.document_admin.add_main_docs(self.mother)
        mother_pk = self.mother.pk
        required = (
            f'<a class="add-change-link disabled-link" href="/admin/documents/document/{mother_pk}/change/?mother={mother_pk}&amp;documents=main">'
        )
        self.assertIn(required, add_new)

    def test_add_change_icon(self):
        request = self.factory.get('/')
        request.user = self.superuser
        self.document_admin.request = request

        add_new = self.document_admin.add_main_docs(self.mother)
        required = (
            '<img src="/static/documents/img/plus.jpeg" class="add-icon"> Add'
        )
        self.assertIn(required, add_new)

        for integer in range(1, 8):
            mock_file = SimpleUploadedFile(f'test{integer}.txt', b'This is a test file', content_type='text/plain')
            MainDocument.objects.create(mother=self.mother, file=mock_file, note=f'some{integer}', title=f'title{integer}')

        add_new = self.document_admin.add_main_docs(self.mother)
        required = (
            '<img src="/static/documents/img/pencil.png" class="change-icon"> Change'
        )
        self.assertIn(required, add_new)
