from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

from mothers.models import Condition
from mothers.services.condition import filter_condition_by_date_time, queryset_with_filter_condition, get_url_query


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
    )

    def response_add(self, request: HttpRequest, obj: Condition, post_url_continue=None) -> HttpResponseRedirect:
        """
        Overrides the response after adding a new 'Condition' instance in the admin.
        If the 'Condition' instance is successfully created and the user hasn't chosen to continue editing
        or add another, this method redirects to the URL specified by the '_changelist_filters' parameter
        in the request. This allows the user to return to the 'Mother' admin page with the same filters applied
        as before they left to add the 'Condition'.
        """
        res = super().response_add(request, obj, post_url_continue)
        if obj and '_continue' not in request.POST and '_addanother' not in request.POST:
            # Check if the '_changelist_filters' parameter is in the request
            return_path = request.GET.get('_changelist_filters')
            if return_path:
                # Redirect to the URL that's been passed in the '_changelist_filters' parameter
                return HttpResponseRedirect(return_path)
        return res

    def response_change(self, request: HttpRequest, obj: Condition) -> HttpResponseRedirect:
        """
        Customizes redirection after editing a 'Condition' instance in the admin interface. The redirection
        depends on the condition's state, scheduling attributes, and the presence of other conditions meeting
        certain criteria.

        The method redirects to various URLs based on several factors:
        - Maintains default behavior for actions like 'Save and continue editing' or 'Save and add another'.
        - Redirects to the 'Mother' admin changelist page with filters applied if '_changelist_filters' are present.
        - Redirects to the 'Mother' changelist page or a filtered version of it, based on the finished status,
          scheduled date, and scheduled time of the condition, and the presence of other conditions meeting
          specific scheduling criteria.

        Returns:
        - HttpResponseRedirect: Redirects to an appropriate URL based on the specified criteria.
        """
        res = super().response_change(request, obj)

        for_date, for_datetime = filter_condition_by_date_time()
        for_date, for_datetime = queryset_with_filter_condition(for_date, for_datetime)

        if '_continue' not in request.POST and '_addanother' not in request.POST:
            return_path = request.GET.get('_changelist_filters')
            if return_path:
                return HttpResponseRedirect(return_path)

            if obj.finished and obj.scheduled_date and obj.scheduled_time and not for_datetime:
                mother_changelist_url = reverse('admin:mothers_mother_changelist')
                return HttpResponseRedirect(mother_changelist_url)

            if obj.finished and obj.scheduled_date and not obj.scheduled_time and not for_date:
                mother_changelist_url = reverse('admin:mothers_mother_changelist')
                return HttpResponseRedirect(mother_changelist_url)

            if obj.finished and obj.scheduled_date and obj.scheduled_time and for_datetime:
                mother_filter_changelist_url = get_url_query(1)
                return HttpResponseRedirect(mother_filter_changelist_url)

            if obj.finished and obj.scheduled_date and not obj.scheduled_time and for_date:
                mother_filter_changelist_url = get_url_query(0)
                return HttpResponseRedirect(mother_filter_changelist_url)

            if not obj.finished and obj.scheduled_date and not obj.scheduled_time:
                mother_filter_changelist_url = get_url_query(0)
                return HttpResponseRedirect(mother_filter_changelist_url)

            if not obj.finished and obj.scheduled_date and obj.scheduled_time:
                mother_filter_changelist_url = get_url_query(1)
                return HttpResponseRedirect(mother_filter_changelist_url)

        return res
