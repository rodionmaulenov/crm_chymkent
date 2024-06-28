from django.contrib.admin.sites import AdminSite
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages.storage.fallback import FallbackStorage

from documents.admin import DocumentProxyAdmin
from documents.models import Document
from mothers.models import Mother

User = get_user_model()


class TestDocumentProxyAdmin(TestCase):
    def setUp(self):
        self.admin_site = AdminSite()
        self.admin = DocumentProxyAdmin(Document, self.admin_site)
        self.factory = RequestFactory()
        self.mother = Mother.objects.create(name='test')
        self.superuser = User.objects.create_superuser(username='admin', password='admin', email='admin@example.com')

    def setup_request(self, url, data=None, method='get'):
        if method.lower() == 'post':
            request = self.factory.post(url, data)
        else:
            request = self.factory.get(url)
        request.user = self.superuser

        # Set up session and messages
        request.session = {}
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        return request

    def test_save_and_continue_editing_redirection(self):
        # Simulate POST request to save and continue editing
        post_data = {
            'name': 'test',
            'age': '30',
            'number': '1234567890',
            'program': 'Test Program',
            'blood': 'O+',
            'maried': 'Yes',
            'citizenship': 'Test Country',
            'residence': 'Test City',
            'height_and_weight': '180cm, 75kg',
            'caesarean': 'No',
            'children_age': '5',
            'bad_habits': 'None',
            'maindocument_set-TOTAL_FORMS': '1',
            'maindocument_set-INITIAL_FORMS': '0',
            'maindocument_set-MIN_NUM_FORMS': '0',
            'maindocument_set-MAX_NUM_FORMS': '1000',
            'maindocument_set-0-id': '',
            'maindocument_set-0-mother': self.mother.pk,
            'maindocument_set-0-title': 'PASSPORT',
            'maindocument_set-0-note': 'Test Note',
            'maindocument_set-0-file': SimpleUploadedFile('test.txt', b'This is a test file',
                                                          content_type='text/plain'),
            'maindocument_set-0-DELETE': '',
            'requireddocument_set-TOTAL_FORMS': '1',
            'requireddocument_set-INITIAL_FORMS': '0',
            'requireddocument_set-MIN_NUM_FORMS': '0',
            'requireddocument_set-MAX_NUM_FORMS': '1000',
            'requireddocument_set-0-id': '',
            'requireddocument_set-0-mother': self.mother.pk,
            'requireddocument_set-0-title': 'BANK ACCOUNT',
            'requireddocument_set-0-note': 'Test Note',
            'requireddocument_set-0-file': SimpleUploadedFile('test2.txt', b'This is another test file',
                                                              content_type='text/plain'),
            'requireddocument_set-0-DELETE': '',
            '_continue': 'Save and continue editing'
        }

        url = reverse('admin:documents_document_change', args=[self.mother.pk])
        request = self.setup_request(url, post_data, method='post')

        response = self.admin.response_change(request, self.mother)

        # Check if the form submission is valid and no template response is returned
        self.assertNotEqual(response.status_code, 200,
                            f"Form errors: {response.context_data['adminform'].form.errors if hasattr(response, 'context_data') else 'No context data available'}")

        # Check that the response is a redirection
        self.assertEqual(response.status_code, 302)

        # Check if the URL is correctly modified
        expected_url = reverse('admin:documents_document_change', args=[self.mother.pk])
        self.assertEqual(response.url, expected_url)

    def test_save_redirection(self):
        # Simulate POST request to save
        post_data = {
            'name': 'test',
            'age': '30',
            'number': '1234567890',
            'program': 'Test Program',
            'blood': 'O+',
            'maried': 'Yes',
            'citizenship': 'Test Country',
            'residence': 'Test City',
            'height_and_weight': '180cm, 75kg',
            'caesarean': 'No',
            'children_age': '5',
            'bad_habits': 'None',
            'maindocument_set-TOTAL_FORMS': '1',
            'maindocument_set-INITIAL_FORMS': '0',
            'maindocument_set-MIN_NUM_FORMS': '0',
            'maindocument_set-MAX_NUM_FORMS': '1000',
            'maindocument_set-0-id': '',
            'maindocument_set-0-mother': self.mother.pk,
            'maindocument_set-0-title': 'PASSPORT',
            'maindocument_set-0-note': 'Test Note',
            'maindocument_set-0-file': SimpleUploadedFile('test.txt', b'This is a test file',
                                                          content_type='text/plain'),
            'maindocument_set-0-DELETE': '',
            'requireddocument_set-TOTAL_FORMS': '1',
            'requireddocument_set-INITIAL_FORMS': '0',
            'requireddocument_set-MIN_NUM_FORMS': '0',
            'requireddocument_set-MAX_NUM_FORMS': '1000',
            'requireddocument_set-0-id': '',
            'requireddocument_set-0-mother': self.mother.pk,
            'requireddocument_set-0-title': 'BANK ACCOUNT',
            'requireddocument_set-0-note': 'Test Note',
            'requireddocument_set-0-file': SimpleUploadedFile('test2.txt', b'This is another test file',
                                                              content_type='text/plain'),
            'requireddocument_set-0-DELETE': '',
            '_save': 'Save'
        }

        url = reverse('admin:documents_document_change', args=[self.mother.pk])
        request = self.setup_request(url, post_data, method='post')

        response = self.admin.response_change(request, self.mother)

        # Check if the form submission is valid and no template response is returned
        self.assertNotEqual(response.status_code, 200,
                            f"Form errors: {response.context_data['adminform'].form.errors if hasattr(response, 'context_data') else 'No context data available'}")

        # Check that the response is a redirection
        self.assertEqual(response.status_code, 302)

        # Check if the URL is correctly modified
        expected_url = reverse('admin:documents_document_changelist')
        self.assertEqual(response.url, expected_url)

    def test_obj_page_redirection(self):
        # Simulate POST request to navigate to the custom URL (_obj_page)
        post_data = {
            'name': 'test',
            'age': '30',
            'number': '1234567890',
            'program': 'Test Program',
            'blood': 'O+',
            'maried': 'Yes',
            'citizenship': 'Test Country',
            'residence': 'Test City',
            'height_and_weight': '180cm, 75kg',
            'caesarean': 'No',
            'children_age': '5',
            'bad_habits': 'None',
            'maindocument_set-TOTAL_FORMS': '1',
            'maindocument_set-INITIAL_FORMS': '0',
            'maindocument_set-MIN_NUM_FORMS': '0',
            'maindocument_set-MAX_NUM_FORMS': '1000',
            'maindocument_set-0-id': '',
            'maindocument_set-0-mother': self.mother.pk,
            'maindocument_set-0-title': 'PASSPORT',
            'maindocument_set-0-note': 'Test Note',
            'maindocument_set-0-file': SimpleUploadedFile('test.txt', b'This is a test file',
                                                          content_type='text/plain'),
            'maindocument_set-0-DELETE': '',
            'requireddocument_set-TOTAL_FORMS': '1',
            'requireddocument_set-INITIAL_FORMS': '0',
            'requireddocument_set-MIN_NUM_FORMS': '0',
            'requireddocument_set-MAX_NUM_FORMS': '1000',
            'requireddocument_set-0-id': '',
            'requireddocument_set-0-mother': self.mother.pk,
            'requireddocument_set-0-title': 'BANK ACCOUNT',
            'requireddocument_set-0-note': 'Test Note',
            'requireddocument_set-0-file': SimpleUploadedFile('test2.txt', b'This is another test file',
                                                              content_type='text/plain'),
            'requireddocument_set-0-DELETE': '',
            '_obj_page': 'Custom URL'
        }

        url = reverse('admin:documents_document_change', args=[self.mother.pk])
        request = self.setup_request(url, post_data, method='post')

        response = self.admin.response_change(request, self.mother)

        # Check if the form submission is valid and no template response is returned
        self.assertNotEqual(response.status_code, 200,
                            f"Form errors: {response.context_data['adminform'].form.errors if hasattr(response, 'context_data') else 'No context data available'}")

        # Check that the response is a redirection
        self.assertEqual(response.status_code, 302)

        # Check if the URL is correctly modified
        expected_url = reverse('admin:documents_document_change', args=[self.mother.pk])
        self.assertEqual(response.url, expected_url)
