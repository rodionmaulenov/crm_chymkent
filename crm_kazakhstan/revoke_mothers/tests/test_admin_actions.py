from django.test import TestCase, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import Permission
from django.http import HttpRequest

from revoke_mothers.admin import RevokeMotherAdmin
from mothers.models import Mother, Comment

Mother: models
Comment: models

User = get_user_model()


class BannedMotherAdminActionTest(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(username='user', password='user', is_staff=True)

        can_view_mother_permission = Permission.objects.get(codename='view_mother')
        self.return_mothers = Permission.objects.get(codename='return_mothers')

        self.staff_user.user_permissions.add(can_view_mother_permission)

        self.mother1 = Mother.objects.create(name='Mother 1', number='123', program='Test Program 1')
        self.mother2 = Mother.objects.create(name='Mother 2', number='456', program='Test Program 2')
        self.mother3 = Mother.objects.create(name='Mother 3', number='678', program='Test Program 3')

        Comment.objects.create(mother=self.mother1, banned=True)
        Comment.objects.create(mother=self.mother2, banned=False)
        Comment.objects.create(mother=self.mother3, banned=True)

        admin_site = AdminSite()
        self.mother_admin = RevokeMotherAdmin(Mother, admin_site)

    def test_make_revoke_action_with_access_another_way(self):
        request = RequestFactory()
        request = request.post('/')
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        queryset = Mother.objects.all()

        comments_before = Comment.objects.filter(mother__in=queryset, banned=True).count()
        self.mother_admin.mother_return(request=request, queryset=queryset)
        comments_after = Comment.objects.filter(mother__in=queryset, banned=False).count()

        self.assertGreater(comments_after, comments_before)

    def test_get_actions_with_permission(self):
        self.staff_user.user_permissions.add(self.return_mothers)
        request = HttpRequest()
        request.user = self.staff_user

        actions = self.mother_admin.get_actions(request)
        self.assertIn('mother_return', actions)

    def test_get_actions_without_permission(self):
        self.staff_user.user_permissions.remove(self.return_mothers)
        request = HttpRequest()
        request.user = self.staff_user

        actions = self.mother_admin.get_actions(request)
        self.assertNotIn('mother_return', actions)
