from django.test import TestCase, RequestFactory
from django.db import models
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse

from mothers.models import Mother, Condition
from mothers.admin import MotherAdmin

Condition: models
User = get_user_model()
Mother: models


class ResponsePostSaveChangeTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.mother_admin = MotherAdmin(Mother, admin.site)

        # Create a user
        self.user = User.objects.create_superuser('admin', 'admin@test.com', 'password')

        # Create a mother instance
        self.mother = Mother.objects.create(name="Test Mother")

    def test_redirect_on_main_changelist(self):
        condition = Condition.objects.create(mother=self.mother, finished=True)

        request = self.factory.get('/admin/mothers/mother/')
        request.GET = {'_changelist_filters': 'date_or_time=by_date'}

        request.user = self.user

        response = self.mother_admin.response_post_save_change(request, self.mother)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(reverse('admin:mothers_mother_changelist')))

        condition.delete()

    def test_redirect_on_filteres_changelist(self):
        condition = Condition.objects.create(mother=self.mother, finished=False)

        request = self.factory.get('/admin/mothers/mother/')
        request.GET = {'_changelist_filters': 'date_or_time=by_date'}

        request.user = self.user

        response = self.mother_admin.response_post_save_change(request, self.mother)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(reverse('admin:mothers_mother_changelist')))

        condition.delete()
