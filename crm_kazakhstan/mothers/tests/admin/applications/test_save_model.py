from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.contrib.auth import get_user_model
from mothers.models import Mother
from mothers.admin import MotherAdmin
from freezegun import freeze_time
from django.contrib import admin

User = get_user_model()


class MotherAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @freeze_time("2024-07-08 12:00:00")
    def test_save_model_sets_utc_time_and_assigns_permission(self):
        # Create a CustomUser with timezone set to UTC
        user = User.objects.create_user(username='testuser', password='12345', timezone='UTC')

        # Create a request object and set the user
        request = self.factory.get('/')
        request.user = user

        # Create a Mother instance (without saving to the database yet)
        mother = Mother(name="Test Mother")

        # Create an instance of the MotherAdmin
        mother_admin = MotherAdmin(Mother, admin.site)

        # Save the Mother instance through the admin interface
        mother_admin.save_model(request, mother, None, False)

        # Refresh the mother instance from the database
        mother.refresh_from_db()

        # Check that the 'created' field is set to the current UTC time
        self.assertEqual(mother.created, timezone.now())

        # Check that the user has the correct permission for the object
        model = mother.__class__.__name__.lower()
        codename = f'{model}_testuser'
        self.assertTrue(user.has_perm(codename, mother))

    @freeze_time("2024-07-08 12:00:00")
    def test_save_model_with_local_time_kiev(self):
        # Set the timezone to Kiev for the user
        kiev_timezone = 'Europe/Kiev'

        # Create a CustomUser with timezone set to Europe/Kiev
        user = User.objects.create_user(username='testuser', password='12345', timezone=kiev_timezone)

        # Create a request object and set the user
        request = self.factory.get('/')
        request.user = user

        # Create a Mother instance (without saving to the database yet)
        mother = Mother(name="Test Mother")

        # Create an instance of the MotherAdmin
        mother_admin = MotherAdmin(Mother, admin.site)

        # Save the Mother instance through the admin interface
        mother_admin.save_model(request, mother, None, False)

        # Refresh the mother instance from the database
        mother.refresh_from_db()

        # Check that the 'created' field is set to the current UTC time
        self.assertEqual(mother.created, timezone.now())

        # Check that the user has the correct permission for the object
        model = mother.__class__.__name__.lower()
        codename = f'{model}_testuser'
        self.assertTrue(user.has_perm(codename, mother))
