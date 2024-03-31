from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from gmail_messages.services.manager_factory import ManagerFactory

from mothers.models import Mother, State, Stage
from mothers.admin import StateAdmin

User = get_user_model()
Mother: models
State: models


class HasChangePermissionTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = StateAdmin(State, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staff_user', password='password', is_staff=True,
                                              stage=Stage.StageChoices.PRIMARY)

    def test_super_user_has_perm_obj_lvl(self):
        mother = Mother.objects.create(name='Mother 1')
        condition = State.objects.create(mother=mother, scheduled_date=timezone.now().date(),
                                         scheduled_time=timezone.now().time())
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_change_permission(request, condition)

        self.assertTrue(view)

    def test_super_user_has_perm_list_layer(self):
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.admin.has_change_permission(request)

        self.assertFalse(view)

    def test_staff_has_perm_if_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        condition = State.objects.create(mother=mother, scheduled_date=timezone.now().date(),
                                         scheduled_time=timezone.now().time())

        factory = ManagerFactory()
        primary_manager = factory.create('PrimaryStageManager')
        primary_manager.assign_user(content_type=self.admin, obj=condition)

        request = self.factory.get('/')
        request.user = self.staff_user

        self.assertTrue(self.admin.has_change_permission(request, condition))

    def test_staff_has_perm_with_model_lvl_perm(self):
        mother = Mother.objects.create(name='Mother 1')
        condition = State.objects.create(mother=mother, scheduled_date=timezone.now().date(),
                                         scheduled_time=timezone.now().time())
        view_permission = Permission.objects.get(codename='change_state')
        self.staff_user.user_permissions.add(view_permission)

        request = self.factory.get('/')
        request.user = self.staff_user

        self.assertTrue(self.admin.has_change_permission(request, condition))

    def test_staff_has_not_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        condition = State.objects.create(mother=mother, scheduled_date=timezone.now().date(),
                                         scheduled_time=timezone.now().time())

        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_change_permission(request, condition)

        self.assertFalse(view)

    def test_staff_user_has_not_perm_list_layer(self):
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.admin.has_change_permission(request)

        self.assertFalse(view)
