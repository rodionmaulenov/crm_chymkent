from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class GetAdminAccessTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create_user(username='staffuser', password='staffuserpassword', is_staff=True)
        self.simple_user = User.objects.create_user(username='user', password='staffuserpassword')

    def test_superuser_has_access_admin_url(self):
        self.client.force_login(self.superuser)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_staff_user_has_access_admin_url(self):
        self.client.force_login(self.staff_user)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_simple_user_has_access_admin_url(self):
        self.client.force_login(self.simple_user)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/login/?next=/admin/')
