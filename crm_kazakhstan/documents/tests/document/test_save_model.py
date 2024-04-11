from guardian.shortcuts import get_perms

from django.db import models
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from documents.admin import DocumentAdmin
from documents.models import Document

from mothers.models import Mother, Stage

User = get_user_model()

Document: models
Mother: models


class SaveModelTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = DocumentAdmin(Document, self.site)
        self.factory = RequestFactory()

        self.mother = Mother.objects.create(name='mother')
        self.mock_file = SimpleUploadedFile('test.txt', b'This is a test file', content_type='text/plain')

        self.staff_user = User.objects.create(username='admin', password='password', is_staff=True,
                                              stage=Stage.StageChoices.PRIMARY)

    def test_when_add_is_assigned_obj_perm_view(self):
        document = Document(mother=self.mother, file=self.mock_file)
        self.assertIsNone(document.pk)

        request = self.factory.get('/')
        request.user = self.staff_user

        form = self.admin.get_form(request)
        self.admin.save_model(request, document, form, change=False)

        self.assertIsNotNone(document.pk)

        self.assertEqual(get_perms(self.staff_user, document), ['primary_document_admin'])
