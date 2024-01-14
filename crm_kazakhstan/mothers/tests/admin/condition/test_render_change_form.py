from django.contrib.admin.helpers import AdminForm
from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model

from mothers.admin import ConditionAdmin
from mothers.models import Condition

User = get_user_model()


class RenderChangeFormMTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = ConditionAdmin(Condition, self.site)
        self.factory = RequestFactory()

        self.superuser = User.objects.create_superuser(username='testuser', email='test@example.com',
                                                       password='top_secret')
        self.staff_user = User.objects.create_user(username='staffuser', password='top_secret')

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
