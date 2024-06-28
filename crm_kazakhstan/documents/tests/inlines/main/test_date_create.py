from datetime import datetime
from django.contrib import admin
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
import pytz
from documents.inlines.main import MainInline
from documents.models import MainDocument
from mothers.models import Mother
from freezegun import freeze_time

User = get_user_model()


class DateCreateTest(TestCase):
    def setUp(self):
        # Create a superuser
        self.user = User.objects.create_superuser(username='admin', password='admin', email='admin@example.com')

        # Create an instance of Mother and MainDocument with a specific datetime
        self.mother = Mother.objects.create(name='Test Mother')

        # Create a request factory and a request
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.user

        # Create an instance of the admin class
        self.admin_instance = MainInline(MainDocument, admin.site)
        self.admin_instance.request = self.request  # Attach request to admin instance

    @freeze_time("2024-05-21 20:00:00")
    def test_date_create(self):
        document = MainDocument.objects.create(
            mother=self.mother,
            title='Test Document',
            file='testfile.txt',
            created=datetime(2024, 5, 20, 20, 0, 0, tzinfo=pytz.utc)
        )
        # Set user's timezone for testing
        self.request.user.timezone = 'Europe/Kiev'

        # Call the method
        result = self.admin_instance.date_create(document)

        # Check if the result is as expected
        expected_result = 'May 2024, 23:00'
        self.assertEqual(result, expected_result)
