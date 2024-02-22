from typing import Dict, Any, Optional, Type, Tuple
from guardian.admin import GuardedModelAdmin

from django.db.models import Field
from django.contrib import admin
from django.contrib.admin.helpers import AdminForm
from django.forms import ModelForm
from django import forms
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

from mothers.admin import MotherAdmin
from mothers.forms import ConditionAdminForm
from mothers.models import Condition, Mother
from mothers.services.condition import is_filtered_condition_met, redirect_to_appropriate_url, extract_choices, \
    filter_choices, inject_request_into_form, convert_to_utc_and_save, assign_permissions_to_user, has_permission, \
    adjust_button_visibility, after_add_message, after_change_message, filters_datetime, filtered_mothers
from mothers.services.mother import get_model_objects


@admin.register(Condition)
class ConditionAdmin(GuardedModelAdmin):
    form = ConditionAdminForm
    fields = ('mother', 'condition', 'reason', 'scheduled_date', 'scheduled_time', 'finished')
    readonly_fields = ('mother',)

    def get_fields(self, request: HttpRequest, obj: Optional[Condition] = None) -> Tuple[str, ...]:
        """
        Define which fields to display on the add and change forms.
        """
        if obj is None:
            # Add form (creating a new instance)
            return 'mother', 'condition', 'reason', 'scheduled_date', 'scheduled_time'
        else:
            # Change form (editing an existing instance)
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
        """Not access to site layer for all."""
        if super().has_module_permission(request):
            return False

    def has_view_permission(self, request: HttpRequest, obj=None) -> bool:
        """Has access only on obj lvl. If has view obj permission or model view lvl permission"""
        return has_permission(self, request, obj, 'view', super().has_view_permission(request, obj))

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        """Has access only on obj lvl. If has change obj permission or model change lvl permission"""
        return has_permission(self, request, obj, 'change', super().has_change_permission(request, obj))

    def has_add_permission(self, request: HttpRequest, obj=None) -> bool:
        """Obviously assign base permission or if mother objects belong to user"""
        mother_admin = MotherAdmin(Mother, admin.site)
        return super().has_add_permission(request) or get_model_objects(mother_admin, request).exists()

    def render_change_form(self, request: HttpRequest, context: Dict[str, Any],
                           add: bool = False, change: bool = False,
                           form_url: str = '', obj: Optional[Condition] = None) -> AdminForm:
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

    def response_add(self, request: HttpRequest, obj: Condition, post_url_continue=None) -> HttpResponseRedirect:
        """
        Called only if last 'Condition' instance related with mother finished equal True.
        This new Page determines based on _changelist_filters or without - filtered change mother list page
        or change mother list page
        """

        return_path = request.GET.get('_changelist_filters')
        if return_path:
            after_add_message(self, request, obj)
            # Redirect to the URL that's been passed in the '_changelist_filters' parameter
            return HttpResponseRedirect(return_path)
        url = reverse('admin:mothers_mother_changelist')
        after_add_message(self, request, obj)
        return HttpResponseRedirect(url)

    def response_change(self, request: HttpRequest, obj: Condition) -> HttpResponseRedirect:
        """
        Customizes the response after editing a 'Condition' instance in the admin interface.
        Redirects to the previous URL if available and valid after the condition is changed.
        If no previous URL is set or if the filtered change list is empty, redirects to the Mother change list page.
        """
        for_datetime = filters_datetime(obj.mother)
        for_datetime = filtered_mothers(for_datetime)

        previous_url = request.session.get('previous_url')
        mother_changelist_url = reverse('admin:mothers_mother_changelist')

        # Check if the previous URL corresponds to a filtered condition
        if is_filtered_condition_met(previous_url, for_datetime):
            after_change_message(self, request, obj)
            return redirect_to_appropriate_url(request, previous_url, mother_changelist_url)
        after_change_message(self, request, obj)
        # Redirect to the Mother change list page if no previous URL is set or valid
        return HttpResponseRedirect(mother_changelist_url)

    def save_model(self, request: HttpRequest, obj: Condition, form: ModelForm, change: bool) -> None:
        """
        Handles the saving of a Condition instance in the Django admin interface.
        Converts scheduled time to UTC, saves the instance, and assigns permissions if it's a new instance.
        """
        convert_to_utc_and_save(request, obj)

        is_new = not obj.pk  # Check if the object is new (has no primary key yet)

        super().save_model(request, obj, form, change)

        if is_new:
            # Assign permission for each new instance of Condition
            assign_permissions_to_user(request.user, obj)

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

        :param db_field: The database field being processed.

        :return: The form field for the given database field.
        """
        if db_field.name == "condition":
            original_choices = extract_choices(db_field)
            # Logic for filtering choices during 'add' action
            # Logic for filtering choices during 'change' action
            filtered_choices = filter_choices(self.current_obj, original_choices)
            kwargs["choices"] = filtered_choices

        return super().formfield_for_choice_field(db_field, request, **kwargs)
