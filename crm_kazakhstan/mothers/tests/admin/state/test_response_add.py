from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from mothers.models import State, Mother
from mothers.admin import StateAdmin

State: models
Mother: models

User = get_user_model()


class ResponseAddMethodTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.condition_admin = StateAdmin(State, AdminSite())
        self.superuser = User.objects.create_superuser(username='user', password='user')

    def test_response_add_with_extra_params(self):
        mother = Mother.objects.create(name='Mother')
        condition = State.objects.create(mother=mother)

        request = self.factory.post(
            '/admin/mothers/condition/add/?_changelist_filters=/admin/mothers/mother/%3Fsomefilter%3Dvalue'
        )
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        response = self.condition_admin.response_add(request, condition)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin:mothers_mother_changelist'))

    def test_response_add(self):
        mother = Mother.objects.create(name='Mother')
        condition = State.objects.create(mother=mother)

        request = self.factory.post('/admin/mothers/condition/add/')
        request.user = self.superuser
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        response = self.condition_admin.response_add(request, condition)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin:mothers_mother_changelist'))
