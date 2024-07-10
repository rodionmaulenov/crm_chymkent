from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from documents.admin import DocumentProxyAdmin
from documents.models import Document, MainDocument
from mothers.models import Mother, Stage

User = get_user_model()

class AddMainDocsTest(TestCase):
    def setUp(self):
        self.document_admin = DocumentProxyAdmin(Document, admin.site)
        self.factory = RequestFactory()
        self.mother = Mother.objects.create(name='test')
        Stage.objects.create(mother=self.mother, stage=Stage.StageChoices.PRIMARY, finished=False)

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.user_with_perm = User.objects.create_user('user', 'user@example.com', 'password')

        # Add 'documents.view_document' permission to the user
        permission = Permission.objects.get(codename='view_document', content_type__app_label='documents')
        self.user_with_perm.user_permissions.add(permission)

    def test_add_document_link_when_document_count_equal_zero_superuser(self):
        request = self.factory.get('/')
        request.user = self.superuser
        self.document_admin.request = request

        add_new = self.document_admin.add_main_docs(self.mother)
        required = (
            f'<a href="/admin/documents/document/{self.mother.pk}/change/?mother={self.mother.pk}&amp;documents=main">0 of 10</a>'
        )
        self.assertIn(required, add_new)

    def test_add_document_link_when_document_count_equal_one_superuser(self):
        MainDocument.objects.create(
            mother=self.mother,
            title=MainDocument.MainDocumentChoice.PASSPORT,
            note='Sample note',
            file='path/to/sample_file.pdf'
        )
        request = self.factory.get('/')
        request.user = self.superuser
        self.document_admin.request = request

        add_new = self.document_admin.add_main_docs(self.mother)
        required = (
            f'<a href="/admin/documents/document/{self.mother.pk}/change/?mother={self.mother.pk}&amp;documents=main">{self.mother.main_document.count()} of 10</a>'
        )
        self.assertIn(required, add_new)

    def test_add_document_count_when_document_count_equal_zero_user_with_perm(self):
        request = self.factory.get('/')
        request.user = self.user_with_perm
        self.document_admin.request = request

        add_new = self.document_admin.add_main_docs(self.mother)
        required = '0'
        self.assertIn(required, add_new)
        self.assertNotIn('<a href=', add_new)

    def test_add_document_count_when_document_count_equal_one_user_with_perm(self):
        MainDocument.objects.create(
            mother=self.mother,
            title=MainDocument.MainDocumentChoice.PASSPORT,
            note='Sample note',
            file='path/to/sample_file.pdf'
        )
        request = self.factory.get('/')
        request.user = self.user_with_perm
        self.document_admin.request = request

        add_new = self.document_admin.add_main_docs(self.mother)
        required = str(self.mother.main_document.count())
        self.assertIn(required, add_new)
        self.assertNotIn('<a href=', add_new)
