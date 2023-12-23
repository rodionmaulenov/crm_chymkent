from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from mothers.models import Mother, Planned
from mothers.admin import PlannedInline

User = get_user_model()


class PlannedInlineTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.factory = RequestFactory()

        # Create a user with the specific permission
        self.user_with_permission = User.objects.create_user('user_with_perm', 'user_with_perm@example.com', 'password')
        permission = Permission.objects.get(codename='to_manager_on_primary_stage')
        self.user_with_permission.user_permissions.add(permission)

        # Create a user without the specific permission
        self.user_without_permission = User.objects.create_user('user_without_perm', 'user_without_perm@example.com',
                                                                'password')

    def test_plan_field_choices_with_permission(self):
        request = self.factory.get('/')
        request.user = self.user_with_permission

        inline = PlannedInline(Mother, self.site)
        formfield = inline.formfield_for_choice_field(Planned._meta.get_field('plan'), request)

        self.assertEqual(formfield.choices,
                         [(Planned.PlannedChoices.TAKE_TESTS.value, Planned.PlannedChoices.TAKE_TESTS.label)])

    def test_plan_field_choices_without_permission(self):
        request = self.factory.get('/')
        request.user = self.user_without_permission

        inline = PlannedInline(Mother, self.site)
        formfield = inline.formfield_for_choice_field(Planned._meta.get_field('plan'), request)

        self.assertEqual(formfield.choices, [])
