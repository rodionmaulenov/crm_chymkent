from django.contrib.admin.helpers import AdminForm
from django.db import models
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model

from ban.admin import BanAdmin
from ban.models import Ban

from mothers.models import Mother, Stage

User = get_user_model()

Mother: models
Ban: models


class RenderChangeFormTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = BanAdmin(Ban, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser(username='superuser', email='test@example.com',
                                                       password='top_secret', stage=Stage.StageChoices.PRIMARY)
        self.staff_user = User.objects.create_user(username='staff_user', password='top_secret',
                                                   stage=Stage.StageChoices.PRIMARY)

    def test_render_change_form_add_for_superuser(self):
        request = self.factory.get('/')
        request.user = self.superuser

        # Set up the complete context that Django admin expects
        form = self.admin.get_form(request)
        admin_form = AdminForm(
            form(), list(self.admin.get_fieldsets(request)),
            self.admin.get_prepopulated_fields(request)
        )

        # Include the required 'inline_admin_formsets' key with an empty list,
        # and 'media' as it's also required by the change form template.
        context = {
            'adminform': admin_form,
            'inline_admin_formsets': [],
            'media': self.admin.media,
            'add': True,
            'change': False,
            'is_popup': False,
            'save_as': False,
            'has_delete_permission': False,
            'has_add_permission': True,
            'has_change_permission': True,
            'has_view_permission': True,
            'has_editable_inline_admin_formsets': False,
        }

        # Call the method you want to test
        response = self.admin.render_change_form(request, context, add=True)

        # Check the response context for the expected changes
        self.assertIn('show_save_and_add_another', response.context_data)
        self.assertFalse(response.context_data['show_save_and_add_another'])
        self.assertIn('show_save_and_continue', response.context_data)
        self.assertFalse(response.context_data['show_save_and_continue'])
        self.assertIn('show_save', response.context_data)
        self.assertTrue(response.context_data['show_save'])

    def test_render_change_form_add_for_staff_user(self):
        request = self.factory.get('/')
        request.user = self.staff_user

        # Set up the complete context that Django admin expects
        form = self.admin.get_form(request)
        admin_form = AdminForm(
            form(), list(self.admin.get_fieldsets(request)),
            self.admin.get_prepopulated_fields(request)
        )

        # Include the required 'inline_admin_formsets' key with an empty list,
        # and 'media' as it's also required by the change form template.
        context = {
            'adminform': admin_form,
            'inline_admin_formsets': [],
            'media': self.admin.media,
            'add': True,
            'change': False,
            'is_popup': False,
            'save_as': False,
            'has_delete_permission': False,
            'has_add_permission': True,
            'has_change_permission': True,
            'has_view_permission': True,
            'has_editable_inline_admin_formsets': False,
        }

        # Call the method you want to test
        response = self.admin.render_change_form(request, context, add=True)

        # Check the response context for the expected changes
        self.assertIn('show_save_and_add_another', response.context_data)
        self.assertFalse(response.context_data['show_save_and_add_another'])
        self.assertIn('show_save_and_continue', response.context_data)
        self.assertFalse(response.context_data['show_save_and_continue'])
        self.assertIn('show_save', response.context_data)
        self.assertTrue(response.context_data['show_save'])

    def test_render_change_form_change_for_superuser(self):
        mother = Mother.objects.create(name='Test Mother')
        ban = Ban.objects.create(mother=mother, comment='comment')

        request = self.factory.get(f'/admin/mothers/condition/{ban.pk}/change/')
        request.user = self.superuser

        form = self.admin.get_form(request, obj=ban)
        admin_form = AdminForm(
            form(instance=ban),
            list(self.admin.get_fieldsets(request, obj=ban)),
            self.admin.get_prepopulated_fields(request, obj=ban)
        )

        context = {
            'adminform': admin_form,
            'inline_admin_formsets': [],
            'media': self.admin.media,
            'add': False,
            'change': True,
            'is_popup': False,
            'save_as': False,
            'has_delete_permission': True,
            'has_add_permission': False,
            'has_change_permission': True,
            'has_view_permission': True,
            'has_editable_inline_admin_formsets': False,
            'original': ban,
        }

        response = self.admin.render_change_form(request, context, change=True, obj=ban)

        self.assertIn('show_save_and_add_another', response.context_data)
        self.assertFalse(response.context_data['show_save_and_add_another'])
        self.assertIn('show_save_and_continue', response.context_data)
        self.assertFalse(response.context_data['show_save_and_continue'])
        self.assertIn('show_save', response.context_data)
        self.assertTrue(response.context_data['show_save'])

    def test_render_change_form_change_for_staff_user(self):
        mother = Mother.objects.create(name='Test Mother')
        ban = Ban.objects.create(mother=mother, comment='comment')

        request = self.factory.get(f'/admin/mothers/condition/{ban.pk}/change/')
        request.user = self.staff_user

        form = self.admin.get_form(request, obj=ban)
        admin_form = AdminForm(
            form(instance=ban),
            list(self.admin.get_fieldsets(request, obj=ban)),
            self.admin.get_prepopulated_fields(request, obj=ban)
        )

        context = {
            'adminform': admin_form,
            'inline_admin_formsets': [],
            'media': self.admin.media,
            'add': False,
            'change': True,
            'is_popup': False,
            'save_as': False,
            'has_delete_permission': True,
            'has_add_permission': False,
            'has_change_permission': True,
            'has_view_permission': True,
            'has_editable_inline_admin_formsets': False,
            'original': ban,
        }

        response = self.admin.render_change_form(request, context, change=True, obj=ban)

        self.assertIn('show_save_and_add_another', response.context_data)
        self.assertFalse(response.context_data['show_save_and_add_another'])
        self.assertIn('show_save_and_continue', response.context_data)
        self.assertFalse(response.context_data['show_save_and_continue'])
        self.assertIn('show_save', response.context_data)
        self.assertTrue(response.context_data['show_save'])
