from django.contrib import admin
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.db import models

from mothers.inlines import StateInline
from mothers.models import Mother, State

User = get_user_model()
Mother: models
State: models


class HasViewPermissionTest(TestCase):
    def setUp(self):
        self.inline_condition = StateInline(Mother, admin.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.staff_user = User.objects.create(username='staffuser', password='password', is_staff=True)

    def test_super_user_has_view_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        state = State.objects.create(mother=mother)
        request = self.factory.get('/')
        request.user = self.superuser
        view = self.inline_condition.has_view_permission(request, state)

        self.assertTrue(view)

    def test_staff_user_has_view_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        state = State.objects.create(mother=mother)
        request = self.factory.get('/')
        request.user = self.staff_user
        view = self.inline_condition.has_view_permission(request, state)

        self.assertTrue(view)

    def test_has_view_perm_obj(self):
        mother = Mother.objects.create(name='Mother 1')
        state = State.objects.create(mother=mother)
        request = self.factory.get('/')
        view = self.inline_condition.has_view_permission(request, state)

        self.assertTrue(view)
