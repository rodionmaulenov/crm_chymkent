from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

from mothers.models import Condition
from mothers.services.condition import filter_condition_by_date_time, queryset_with_filter_condition, \
    is_filtered_condition_met, redirect_to_appropriate_url


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
    )

    def response_add(self, request: HttpRequest, obj: Condition, post_url_continue=None) -> HttpResponseRedirect:
        """
        Return on Previous Page after adding new 'Condition' instance.
        This new Page determines based on _changelist_filters or without - filtered change mother list page
        or change mother list page
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
