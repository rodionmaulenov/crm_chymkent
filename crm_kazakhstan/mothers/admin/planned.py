from typing import Dict, Any, Optional, Tuple, Type

from django.contrib import admin
from django.contrib.admin.helpers import AdminForm
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.forms import ModelForm

from mothers.admin import MotherAdmin
from mothers.forms import PlannedAdminForm
from mothers.models import Planned, Mother
from mothers.services.mother import get_model_objects, on_primary_stage
from mothers.services.state import convert_to_utc_and_save, has_permission, adjust_button_visibility, \
    inject_request_into_form

from gmail_messages.services.manager_factory import ManagerFactory

User = get_user_model()


@admin.register(Planned)
class PlannedAdmin(admin.ModelAdmin):
    form = PlannedAdminForm
    fields = ('mother', 'plan', 'note', 'scheduled_date', 'scheduled_time', "created", 'finished')
    readonly_fields = ('mother', 'created')

    def get_fields(self, request: HttpRequest, obj: Optional[Planned] = None) -> Tuple[str, ...]:
        """
        Define which fields to display on the add and change forms.
        """
        if obj is None:
            return 'mother', 'plan', 'note', 'scheduled_date', 'scheduled_time'
        else:
            return 'mother', 'plan', 'note', 'scheduled_date', 'scheduled_time', "created", 'finished'

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
                           form_url: str = '', obj: Optional[Planned] = None) -> AdminForm:
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

    def save_model(self, request: HttpRequest, obj: Planned, form: ModelForm, change: bool) -> None:
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

    def get_form(self, request: HttpRequest, obj=None, **kwargs) -> Type[ModelForm]:
        """
        Request attribute inject into form instance.
        """
        form = super().get_form(request, obj, **kwargs)

        # Return the form class with the request injected into its kwargs.
        return inject_request_into_form(form, request)

    def has_module_permission(self, request: HttpRequest) -> bool:
        """
        Access is denied to everyone.
        """
        base = super().has_module_permission(request)
        if base:
            return False
        return False

    def has_view_permission(self, request: HttpRequest, obj: Planned = None) -> bool:
        return has_permission(self, request, 'view', obj, )

    def has_change_permission(self, request: HttpRequest, obj: Planned = None) -> bool:
        return has_permission(self, request, 'change', obj)

    def has_add_permission(self, request: HttpRequest) -> bool:
        mother_admin = MotherAdmin(Mother, admin.site)
        stage = request.user.stage

        data = get_model_objects(mother_admin, request, stage)
        users_mothers = on_primary_stage(data).exists()

        base_case = super().has_add_permission(request)

        return base_case or users_mothers
