from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.db import models
from django.urls import reverse
from django.utils.http import urlencode

from mothers.models import Mother
from mothers.admin import MotherAdmin

Mother: models


class CreateConditionLinkTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.mother_admin = MotherAdmin(Mother, AdminSite())

    def test_with_no_filters(self):
        mother = Mother.objects.create(name="Test Name")

        request = self.factory.get('/admin/mothers/mother/')

        self.mother_admin.request = request
        link = self.mother_admin.create_condition_link(mother)

        expected_url = reverse('admin:mothers_condition_add')
        current_path_encoded = urlencode({'_changelist_filters': '/admin/mothers/mother/'})
        expected_html = f'<a href="{expected_url}?mother={mother.pk}&{current_path_encoded}">state</a>'

        self.assertEqual(link, expected_html)

    def test_with_various_filters(self):
        mother = Mother.objects.create(name="Test Name")
        filter_query = '?o=3&name__icontains=test'

        # Mock request with filters
        request = self.factory.get(f'/admin/mothers/mother/{filter_query}')

        self.mother_admin.request = request
        link = self.mother_admin.create_condition_link(mother)

        # Expected URL with encoded filters
        current_path_encoded = urlencode({'_changelist_filters': f'/admin/mothers/mother/{filter_query}'})
        expected_url = reverse('admin:mothers_condition_add')
        expected_html = f'<a href="{expected_url}?mother={mother.pk}&{current_path_encoded}">state</a>'

        self.assertEqual(link, expected_html)

    def test_with_special_characters_in_filters(self):
        mother = Mother.objects.create(name="Test Name")
        special_filter_query = '?name__icontains=special%20&char'

        request = self.factory.get(f'/admin/mothers/mother/{special_filter_query}')

        self.mother_admin.request = request
        link = self.mother_admin.create_condition_link(mother)

        current_path_encoded = urlencode({'_changelist_filters': f'/admin/mothers/mother/{special_filter_query}'})
        expected_url = reverse('admin:mothers_condition_add')
        expected_html = f'<a href="{expected_url}?mother={mother.pk}&{current_path_encoded}">state</a>'

        self.assertEqual(link, expected_html)

    def test_with_invalid_mother(self):
        request = self.factory.get('/admin/mothers/mother/')

        self.mother_admin.request = request

        with self.assertRaises(AttributeError):
            self.mother_admin.create_condition_link(None)


