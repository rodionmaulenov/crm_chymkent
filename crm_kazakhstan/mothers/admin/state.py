from typing import Dict, Any, Optional, Type, Tuple, Final
from guardian.admin import GuardedModelAdmin

from django.db.models import Field
from django.contrib import admin, messages
from django.contrib.admin.helpers import AdminForm
from django.forms import ModelForm
from django import forms
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

from mothers.admin import MotherAdmin
from mothers.forms import StateAdminForm
from mothers.models import State, Mother
from mothers.services.mother_classes.permissions import PermissionCheckerFactory
from mothers.services.state import extract_choices, filter_choices, inject_request_into_form, \
    convert_to_utc_and_save, adjust_button_visibility
from mothers.services.mother import on_primary_stage, redirect_to

from gmail_messages.services.manager_factory import ManagerFactory

CLASS_NAME: Final[str] = 'ObjectLevel'


@admin.register(State)
class StateAdmin(GuardedModelAdmin):
    form = StateAdminForm
    fields = ('mother', 'condition', 'reason', 'scheduled_date', 'scheduled_time', 'finished')
    readonly_fields = ('mother',)

    class Media:
        css = {
            'all': ('mothers/css/hide-timezone-time.css',)
        }

    def get_fields(self, request: HttpRequest, obj: Optional[State] = None) -> Tuple[str, ...]:
        """
        Define which fields to display on the add and change forms.
        """
        if obj is None:
            return 'mother', 'condition', 'reason', 'scheduled_date', 'scheduled_time'
        else:
            return 'mother', 'condition', 'reason', 'scheduled_date', 'scheduled_time', 'finished'

    def get_readonly_fields(self, request: HttpRequest, obj=None) -> Tuple[str, ...]:
        """
        Determine the readonly fields based on whether an object is being added or changed.
        """
        if obj:  # This is the change page
            return self.readonly_fields
        else:  # This is the add page
            return ()

    def has_module_permission(self, request: HttpRequest) -> bool:
        """
        Access is denied to everyone.
        """
        base = super().has_module_permission(request)
        if base:
            return False
        return False

    def has_view_permission(self, request: HttpRequest, state: State = None) -> bool:
        permission_checker = PermissionCheckerFactory.get_checker(self, request, CLASS_NAME, 'view')
        has_perm = permission_checker.has_permission(obj=state)
        return has_perm

    def has_change_permission(self, request: HttpRequest, state: State = None) -> bool:
        permission_checker = PermissionCheckerFactory.get_checker(self, request, CLASS_NAME, 'change')
        has_perm = permission_checker.has_permission(obj=state)
        return has_perm

    def has_add_permission(self, request: HttpRequest) -> bool:
        base = super().has_add_permission(request)

        mother_admin = MotherAdmin(Mother, admin.site)
        class_name = 'ModuleLevel'
        permission_checker = PermissionCheckerFactory.get_checker(mother_admin, request, class_name)
        has_perm = permission_checker.has_permission(base, on_primary_stage)
        return has_perm

    def render_change_form(self, request: HttpRequest, context: Dict[str, Any],
                           add: bool = False, change: bool = False,
                           form_url: str = '', obj: Optional[State] = None) -> AdminForm:
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

    @staticmethod
    def handle_redirect(request: HttpRequest, obj: State, text: str) -> HttpResponseRedirect:
        """
        Handles the redirection logic after adding or changing an object.
        """
        path_dict = {
            'message_url': reverse('admin:mothers_mother_change', args=[obj.mother.id]),
            'base_url': reverse('admin:mothers_mother_changelist')
        }
        return redirect_to(request, obj, text, path_dict, messages.SUCCESS)

    def response_add(self, request: HttpRequest, obj: State, post_url_continue=None) -> HttpResponseRedirect:
        """
        After add redirect on mother change list.

        As well if changelist has been filtered before add statement,
        it redirects on this filtered change list page.
        """
        text = f'{obj}, successfully added for'
        return self.handle_redirect(request, obj, text)

    def response_change(self, request: HttpRequest, obj: State) -> HttpResponseRedirect:
        """
        After change redirect on mother change list.

        As well if changelist has been filtered before add statement,
        it redirects on this filtered change list page.
        """
        text = f'{obj}, successfully added for'
        return self.handle_redirect(request, obj, text)

    def save_model(self, request: HttpRequest, obj: State, form: ModelForm, change: bool) -> None:
        """
        Handles the saving of a Condition instance in the Django admin interface.
        Converts scheduled time to UTC, saves the instance, and assigns permissions if it's a new instance.
        """
        convert_to_utc_and_save(request, obj)

        is_new = not obj.pk  # Check if the object is new (has no primary key yet)

        super().save_model(request, obj, form, change)

        if is_new:
            # Assign permission for each new instance of Condition
            user = request.user

            factory = ManagerFactory()
            primary_manager = factory.create('PrimaryStageManager')
            primary_manager.assign_user(content_type=self, obj=obj, user=user)

    def get_form(self, request: HttpRequest, obj=None, **kwargs) -> Type[forms.ModelForm]:
        """
        Current object as attribute add to 'formfield_for_choice_field' and request attribute inject into form instance.
        """
        # Store the current object for use in formfield_for_choice_field.
        self.current_obj = obj

        form = super().get_form(request, obj, **kwargs)

        # Return the form class with the request injected into its kwargs.
        return inject_request_into_form(form, request)

    def formfield_for_choice_field(self, db_field: Field, request: HttpRequest, **kwargs) -> Any:
        """
        Customizes the form field for choice fields. Specifically, it alters the choices for the 'condition' field
        based on whether it's an 'add' or 'change' action.
        """
        if db_field.name == "condition":
            original_choices = extract_choices(db_field)
            # Logic for filtering choices during 'add' action
            # Logic for filtering choices during 'change' action
            filtered_choices = filter_choices(self.current_obj, original_choices)
            kwargs["choices"] = filtered_choices

        return super().formfield_for_choice_field(db_field, request, **kwargs)
