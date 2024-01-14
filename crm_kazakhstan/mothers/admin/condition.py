from typing import Dict, Any, Optional

from django.contrib import admin, messages
from django.contrib.admin.helpers import AdminForm
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

from mothers.models import Condition
from mothers.services.condition import filter_condition_by_date_time, queryset_with_filter_condition, \
    is_filtered_condition_met, redirect_to_appropriate_url


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):

    def has_module_permission(self, request: HttpRequest) -> bool:
        """
        Not access to first layer for all.
        """
        if super().has_module_permission(request):
            return False

    def has_permission(self, request: HttpRequest, obj: Condition, action: str) -> bool:
        """
        list layer:
        Always denied.
        Obj layer:
        If superuser True else user has perms on object or not.
        """
        _meta = self.opts
        code_name = f'{action}_{_meta.model_name}'
        if obj:
            return request.user.has_perm(f'{_meta.app_label}.{code_name}', obj)
        else:
            return False

    def has_view_permission(self, request: HttpRequest, obj=None) -> bool:
        return self.has_permission(request, obj, 'view')

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return self.has_permission(request, obj, 'view')

    def has_add_permission(self, request: HttpRequest, obj=None) -> bool:
        return request.user.groups.filter(name='primary_stage').exists() or request.user.is_superuser

    def render_change_form(self, request: HttpRequest, context: Dict[str, Any],
                           add: bool = False, change: bool = False,
                           form_url: str = '', obj: Optional[Condition] = None) -> AdminForm:
        """
        Override the method to modify the context for the change form template.

        This method is called before the admin form is rendered and allows us to
        alter the context dictionary that is passed to the template.
        """
        # If we are adding a new instance (not changing), adjust the visibility of buttons.
        if add:
            context['show_save_and_add_another'] = False  # Remove "Save and add another" button
            context['show_save_and_continue'] = False  # Remove "Save and continue editing" button
            context['show_save'] = True  # Ensure "Save" button is visible

        # Call the super method with the updated context.
        return super().render_change_form(request, context, add=add, change=change,
                                          form_url=form_url, obj=obj)

    def response_add(self, request: HttpRequest, obj: Condition, post_url_continue=None) -> HttpResponseRedirect:
        """
        Called only if last 'Condition' instance related with mother finished equal True.
        This new Page determines based on _changelist_filters or without - filtered change mother list page
        or change mother list page
        """
        res = super().response_add(request, obj, post_url_continue)
        return_path = request.GET.get('_changelist_filters')
        if return_path:
            # Redirect to the URL that's been passed in the '_changelist_filters' parameter
            return HttpResponseRedirect(return_path)
        return res

    def response_change(self, request: HttpRequest, obj: Condition) -> HttpResponseRedirect:
        """
        Customizes the response after editing a 'Condition' instance in the admin interface.
        Redirects to the previous URL if available and valid after the condition is changed.
        If no previous URL is set or if the filtered change list is empty, redirects to the Mother change list page.
        """
        for_date, for_datetime = filter_condition_by_date_time()
        for_date, for_datetime = queryset_with_filter_condition(for_date, for_datetime)

        previous_url = request.session.get('previous_url')
        mother_changelist_url = reverse('admin:mothers_mother_changelist')

        # Check if the previous URL corresponds to a filtered condition
        if is_filtered_condition_met(previous_url, for_date, for_datetime):
            return redirect_to_appropriate_url(request, previous_url, mother_changelist_url)

        # Redirect to the Mother change list page if no previous URL is set or valid
        return HttpResponseRedirect(mother_changelist_url)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            # Custom message for update
            self.message_user(request, "Your custom change message", messages.SUCCESS)
        else:
            # Custom message for add
            self.message_user(request, "Your custom add message", messages.SUCCESS)
