from django.contrib.admin.sites import AdminSite
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from documents.admin import DocumentProxyAdmin
from documents.models import DocumentProxy

from mothers.models import Mother

User = get_user_model()


class TestDocumentProxyAdmin(TestCase):
    def setUp(self):
        self.admin_site = AdminSite()
        self.admin = DocumentProxyAdmin(DocumentProxy, self.admin_site)
        self.factory = RequestFactory()
        self.mother = Mother.objects.create(name='test')
        self.staff_user = User.objects.create_superuser(username='admin', password='admin', email='admin@example.com')

        self.client = Client()
        self.client.login(username='admin', password='admin')

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

        response = self.client.post(reverse('admin:documents_documentproxy_change', args=[self.mother.pk]), post_data)

        if response.status_code == 200 and hasattr(response, 'context_data'):
            print("Form errors:", response.context_data['adminform'].form.errors)
            if 'inline_admin_formsets' in response.context_data:
                for inline_admin_formset in response.context_data['inline_admin_formsets']:
                    print("Inline formset errors:", inline_admin_formset.formset.errors)
                    for form in inline_admin_formset.formset.forms:
                        print("Inline form data:", form.cleaned_data)
                        print("Inline form errors:", form.errors)
            print("Response content:", response.content.decode())

        # Check if the form submission is valid and no template response is returned
        self.assertNotEqual(response.status_code, 200,
                            f"Form errors: {response.context_data['adminform'].form.errors if hasattr(response, 'context_data') else 'No context data available'}")

        # Check that the response is a redirection
        self.assertEqual(response.status_code, 302)

        # Check if the URL is correctly modified
        expected_url = reverse('admin:documents_documentproxy_change', args=[self.mother.pk])
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

        response = self.client.post(reverse('admin:documents_documentproxy_change', args=[self.mother.pk]), post_data)

        if response.status_code == 200 and hasattr(response, 'context_data'):
            print("Form errors:", response.context_data['adminform'].form.errors)
            if 'inline_admin_formsets' in response.context_data:
                for inline_admin_formset in response.context_data['inline_admin_formsets']:
                    print("Inline formset errors:", inline_admin_formset.formset.errors)
                    for form in inline_admin_formset.formset.forms:
                        print("Inline form data:", form.cleaned_data)
                        print("Inline form errors:", form.errors)
            print("Response content:", response.content.decode())

        # Check if the form submission is valid and no template response is returned
        self.assertNotEqual(response.status_code, 200,
                            f"Form errors: {response.context_data['adminform'].form.errors if hasattr(response, 'context_data') else 'No context data available'}")

        # Check that the response is a redirection
        self.assertEqual(response.status_code, 302)

        # Check if the URL is correctly modified
        expected_url = reverse('admin:documents_documentproxy_changelist')
        self.assertEqual(response.url, expected_url)
