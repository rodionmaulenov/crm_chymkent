from typing import Optional, Tuple, Dict, Any

from django.contrib import admin, messages
from django.urls import reverse
from django.http import HttpRequest, HttpResponseRedirect
from django.db.models import QuerySet
from django.forms import ModelForm
from django.contrib.admin.helpers import AdminForm
from django.db import models

from ban.models import Ban

from gmail_messages.services.manager_factory import ManagerFactory

from mothers.admin import MotherAdmin
from mothers.forms import BanAdminForm
from mothers.models import Mother
from mothers.services.mother_classes.command_interface import ResponseAddBanCommand
from mothers.services.mother_classes.permissions import PermissionCheckerFactory
from mothers.services.state import adjust_button_visibility

Mother: models


@admin.register(Ban)
class BanAdmin(admin.ModelAdmin):
    form = BanAdminForm
    fields = ('mother', 'comment')
    readonly_fields = ('mother',)

    def get_fields(self, request: HttpRequest, obj: Optional[Ban] = None) -> Tuple[str, ...]:
        """
        Define which fields to display on the add and change forms.
        """
        if obj is None:
            return 'mother', 'comment'
        else:
            return ()

    def get_readonly_fields(self, request: HttpRequest, obj=None) -> Tuple[str, ...]:
        """
        Determine the readonly fields based on whether an object is being added or changed.
        """
        if obj:  # This is the change page
            return self.readonly_fields
        else:  # This is the add page
            return ()

    def render_change_form(self, request: HttpRequest, context: Dict[str, Any],
                           add: bool = False, change: bool = False,
                           form_url: str = '', obj: Optional[Ban] = None) -> AdminForm:
        """
        Override the method to modify the context for the change form template.

        This method is called before the admin form is rendered and allows us to
        alter the context dictionary that is passed to the template. The visibility
        of the "Save and add another" and "Save and continue editing" buttons is
        controlled based on whether a new instance is being added or an existing
        instance is being changed.
        """

        adjust_button_visibility(context, add, change)

        # Render the change form with the adjusted context
        return super().render_change_form(request, context, add=add, change=change,
                                          form_url=form_url, obj=obj)

    def save_model(self, request: HttpRequest, obj: Ban, form: ModelForm, change: bool) -> None:
        """
        Handles the saving of a Ban instance in the Django admin interface.
        Assigns permissions if it's a new instance.
        """
        is_new = not obj.pk  # Check if the object is new (has no primary key yet)
        super().save_model(request, obj, form, change)

        if is_new:
            # Assign permission for each new instance of Condition
            user = request.user

            factory = ManagerFactory()
            primary_manager = factory.create('PrimaryStageManager')
            primary_manager.assign_user(content_type=self, obj=obj, user=user)

    def has_module_permission(self, request: HttpRequest) -> bool:
        """
        Access is denied to everyone.
        """
        base = super().has_module_permission(request)
        if base:
            return False
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        self.request = request

        queryset = super().get_queryset(request)
        return queryset

    def has_view_permission(self, request: HttpRequest, ban: Ban = None) -> bool:
        class_name = 'ObjectLevel'
        permission_checker = PermissionCheckerFactory.get_checker(self, request, class_name, 'view')
        has_perm = permission_checker.has_permission(obj=ban)
        return has_perm

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request: HttpRequest, ban: Ban = None) -> bool:
        base = super().has_add_permission(request)

        mother_admin = MotherAdmin(Mother, admin.site)
        class_name = 'ModuleLevel'
        permission_checker = PermissionCheckerFactory.get_checker(mother_admin, request, class_name)
        has_perm = permission_checker.has_permission(base)
        return has_perm

    def response_add(self, request: HttpRequest, obj: Ban, post_url_continue=None) -> HttpResponseRedirect:
        """
        Change stage for mother instance and then redirect on main page.
        """
        path_dict = {
            'message_url': reverse('admin:mothers_mother_change', args=[obj.mother.id]),
            'base_url': reverse('admin:mothers_mother_changelist')
        }

        command = ResponseAddBanCommand(request, obj, path_dict)
        text = 'Successfully transferred to ban'
        return command.execute(text, messages.SUCCESS)
