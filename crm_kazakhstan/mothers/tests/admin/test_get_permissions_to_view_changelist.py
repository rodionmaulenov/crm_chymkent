from django.urls import reverse
from django.contrib.auth.models import Permission
from django.test import TestCase

from django.contrib.auth import get_user_model

User = get_user_model()


class GetAccessViewChangeListTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create_user(username='staffuser', password='staffuserpassword', is_staff=True)
        self.simple_user = User.objects.create_user(username='user', password='staffuserpassword')

        self.view_permission_mother_model = Permission.objects.get(
            codename='view_mother', content_type__app_label='mothers')

    def test_superuser_access(self):
        # Log in as the regular user
        self.client.force_login(self.superuser)

        # Attempt to access the admin page for MyModel
        url = reverse('admin:mothers_mother_changelist')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_staff_user_access_without_perm_view(self):
        # Log in as the regular user
        self.client.force_login(self.staff_user)

        # Attempt to access the admin page for MyModel
        url = reverse('admin:mothers_mother_changelist')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_staff_user_access_with_perm_view(self):
        # Log in as the regular user
        self.staff_user.user_permissions.add(self.view_permission_mother_model)
        self.client.force_login(self.staff_user)

        # Attempt to access the admin page for MyModel
        url = reverse('admin:mothers_mother_changelist')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_simple_user_access_without_perm_view(self):
        self.client.force_login(self.staff_user)

        # Attempt to access the admin page for MyModel
        url = reverse('admin:mothers_mother_changelist')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_simple_user_access_with_perm_view(self):
        self.simple_user.user_permissions.add(self.view_permission_mother_model)
        self.client.force_login(self.simple_user)

        # Attempt to access the admin page for MyModel
        url = reverse('admin:mothers_mother_changelist')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
