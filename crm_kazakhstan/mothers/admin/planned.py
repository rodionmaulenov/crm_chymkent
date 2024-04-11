from typing import Dict, Any, Optional, Tuple, Type

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin.helpers import AdminForm
from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponseRedirect
from django.forms import ModelForm
from django.urls import reverse

from mothers.admin import MotherAdmin
from mothers.forms import PlannedAdminForm
from mothers.models import Planned, Mother
from mothers.services.mother import on_primary_stage, convert_utc_to_local
from mothers.services.mother_classes.formatter_interface import DayMonthYearFormatter, HourMinuteFormatter
from mothers.services.mother_classes.permissions import PermissionCheckerFactory
from mothers.services.state import convert_to_utc_and_save, adjust_button_visibility, inject_request_into_form

from gmail_messages.services.manager_factory import ManagerFactory


User = get_user_model()

CLASS_NAME = 'ObjectLevelPermission'


@admin.register(Planned)
class PlannedAdmin(admin.ModelAdmin):
    form = PlannedAdminForm
    fields = ('mother', 'plan', 'note', 'scheduled_date', 'scheduled_time', 'finished')
    readonly_fields = ('mother', 'display_date', 'display_time', 'display_plan')

    class Media:
        css = {
            'all': ('mothers/css/hide-timezone-time.css',)
        }

    def get_queryset(self, request):
        self.request = request

        queryset = super().get_queryset(request).select_related('mother')
        return queryset

    def get_fields(self, request: HttpRequest, obj: Optional[Planned] = None) -> Tuple[str, ...]:
        """
        Define which fields to display on the add and change forms.
        """
        if obj is None:
            # This is the add form, include 'scheduled_date' and 'scheduled_time'
            return 'mother', 'plan', 'note', 'scheduled_date', 'scheduled_time'
        else:
            # This is the change form, include 'display_date' and 'display_time' as read-only
            return 'mother', 'display_plan', 'note', 'display_date', 'display_time', 'finished'

    def get_readonly_fields(self, request: HttpRequest, obj=None) -> Tuple[str, ...]:
        """
        Determine the readonly fields based on whether an object is being added or changed.
        """
        if obj:  # This is the change page
            return 'mother', 'display_plan', 'note', 'display_date', 'display_time'
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

    def has_view_permission(self, request: HttpRequest, planned: Planned = None) -> bool:
        permission_checker = PermissionCheckerFactory.get_checker(self, request, CLASS_NAME)
        has_perm = permission_checker.has_permission('view', obj=planned)
        return has_perm

    def has_change_permission(self, request: HttpRequest, planned: Planned = None) -> bool:
        permission_checker = PermissionCheckerFactory.get_checker(self, request, CLASS_NAME)
        has_perm = permission_checker.has_permission('change', obj=planned)
        return has_perm

    def has_add_permission(self, request: HttpRequest) -> bool:
        base = super().has_add_permission(request)

        mother_admin = MotherAdmin(Mother, admin.site)
        class_name = 'ModulePermission'
        permission_checker = PermissionCheckerFactory.get_checker(mother_admin, request, class_name)
        has_perm = permission_checker.has_permission(base, on_primary_stage)
        return has_perm

    def response_add(self, request: HttpRequest, obj: Planned, post_url_continue=None) -> HttpResponseRedirect:
        """
        After add redirect ot mother changelist page.
        """
        mother_changelist = reverse('admin:mothers_mother_changelist')
        return HttpResponseRedirect(mother_changelist)

    @admin.display(description='plan')
    def display_plan(self, planned: Planned):
        return format_html('<strong>{}</strong>', planned.get_plan_display().upper())

    @admin.display(description='scheduled date')
    def display_date(self, planned: Planned):
        local_time = convert_utc_to_local(self.request, planned.scheduled_date, planned.scheduled_time)
        formatter = DayMonthYearFormatter()
        formatting = formatter.format(local_time)
        return formatting

    @admin.display(description='scheduled time')
    def display_time(self, planned: Planned):
        local_time = convert_utc_to_local(self.request, planned.scheduled_date, planned.scheduled_time)
        formatter = HourMinuteFormatter()
        formatting = formatter.format(local_time)
        return formatting
