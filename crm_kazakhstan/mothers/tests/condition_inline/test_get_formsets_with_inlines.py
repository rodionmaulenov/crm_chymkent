from django.db import models
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model

from mothers.inlines import ConditionInline, ConditionInlineFormWithFinished, ConditionInlineFormWithoutFinished
from mothers.models import Mother
from mothers.admin import MotherAdmin

User = get_user_model()
Mother: models


class GetSpecificFieldsTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.factory = RequestFactory()
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.mother_admin = MotherAdmin(Mother, self.site)
        self.mother = Mother.objects.create(name='Test Mother')

    def test_dynamic_inline_form_by_date(self):
        request = self.factory.get('/')
        request.GET = {'_changelist_filters': 'date_or_time=by_date'}
        request.user = self.admin_user

        for formset, inline in self.mother_admin.get_formsets_with_inlines(request, self.mother):
            if isinstance(inline, ConditionInline):
                self.assertEqual(inline.form, ConditionInlineFormWithFinished)

    def test_dynamic_inline_form_by_date_and_time(self):
        request = self.factory.get('/')
        request.GET = {'_changelist_filters': 'date_or_time=by_date_and_time'}
        request.user = self.admin_user

        for formset, inline in self.mother_admin.get_formsets_with_inlines(request, self.mother):
            if isinstance(inline, ConditionInline):
                self.assertEqual(inline.form, ConditionInlineFormWithFinished)

    def test_dynamic_inline_form(self):
        request = self.factory.get('/')
        request.user = self.admin_user

        for formset, inline in self.mother_admin.get_formsets_with_inlines(request, self.mother):
            if isinstance(inline, ConditionInline):
                self.assertNotEquals(inline.form, ConditionInlineFormWithFinished)
                self.assertEqual(inline.form, ConditionInlineFormWithoutFinished)
