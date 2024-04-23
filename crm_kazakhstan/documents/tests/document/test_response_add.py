from urllib.parse import urlencode

from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages import get_messages
from django.contrib import admin
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db import models
from django.core.files.uploadedfile import SimpleUploadedFile

from documents.admin import DocumentAdmin
from documents.models import Document

from mothers.models import Mother, Stage

User = get_user_model()

Mother: models
Document: models


class ResponseAddTest(TestCase):
    def setUp(self):
        self.admin = DocumentAdmin(Document, admin.site)
        self.factory = RequestFactory()

        self.mother = Mother.objects.create(name='mother')
        self.mock_file = SimpleUploadedFile('test.txt', b'This is a test file', content_type='text/plain')
        self.document = Document.objects.create(mother=self.mother, file=self.mock_file, note='some', title='some')

        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True,
                                              stage=Stage.StageChoices.PRIMARY)

    def test_url_without_queries(self):
        url = 'admin/documents/document_proxy/'
        query = urlencode({'mother': 1})

        request = self.factory.get(url + '?' + query)

        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request._messages = FallbackStorage(request)
        request.user = self.staff_user

        response = self.admin.response_add(request, self.document)
        required = "/admin/documents/documentproxy/"
        self.assertEqual(response.url, required)
        self.assertEqual(response.status_code, 302)

        messages = list(get_messages(request))
        expected_message = (f'Some, successfully added for <a href="/admin/mothers/'
                            f'mother/{self.mother.id}/change/" ><b>mother</b></a>')
        self.assertIn(expected_message, str(messages[0]))

    def test_url_with_queries(self):
        url = 'admin/documents/document_proxy/'
        query = urlencode({'mother': 1, 'papa': 'karlo'})

        request = self.factory.get(url + '?' + query)

        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        request._messages = FallbackStorage(request)
        request.user = self.staff_user

        response = self.admin.response_add(request, self.document)
        required = "/admin/documents/documentproxy/?papa=karlo"
        self.assertEqual(response.url, required)
        self.assertEqual(response.status_code, 302)

        messages = list(get_messages(request))
        expected_message = (f'Some, successfully added for <a href="/admin/mothers/'
                            f'mother/{self.mother.id}/change/" ><b>mother</b></a>')
        self.assertIn(expected_message, str(messages[0]))

