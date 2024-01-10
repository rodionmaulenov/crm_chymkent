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
        First verifying from what url went to change 'Conditiotn'
        """
        res = super().response_change(request, obj)

        for_date, for_datetime = filter_condition_by_date_time()
        for_date, for_datetime = queryset_with_filter_condition(for_date, for_datetime)
        if '_continue' not in request.POST and '_addanother' not in request.POST:

            # in this case mother instance locate on:
            # [{'date_or_time': 'by_date'}, {'date_or_time': 'by_date_and_time'}]
            if obj.finished and obj.scheduled_date and obj.scheduled_time and not for_datetime:
                mother_changelist_url = reverse('admin:mothers_mother_changelist')
                return HttpResponseRedirect(mother_changelist_url)

            if obj.finished and obj.scheduled_date and not obj.scheduled_time and not for_date:
                mother_changelist_url = reverse('admin:mothers_mother_changelist')
                return HttpResponseRedirect(mother_changelist_url)

            # in this case mother instance locate on one of this urls:
            # [{'date_or_time': 'by_date'}, {'date_or_time': 'by_date_and_time'}]
            if obj.finished and obj.scheduled_date and obj.scheduled_time and for_datetime:
                mother_filter_changelist_url = get_url_query(1)
                return HttpResponseRedirect(mother_filter_changelist_url)

            if obj.finished and obj.scheduled_date and not obj.scheduled_time and for_date:
                mother_filter_changelist_url = get_url_query(0)
                return HttpResponseRedirect(mother_filter_changelist_url)

            # in this case mother instance locate on one of this urls:
            # [{'date_or_time': 'by_date'}, {'date_or_time': 'by_date_and_time'}]
            # and on mother_changelist_url = reverse('admin:mothers_mother_changelist')
            if not obj.finished and obj.scheduled_date and not obj.scheduled_time:
                mother_filter_changelist_url = get_url_query(0)
                return HttpResponseRedirect(mother_filter_changelist_url)

            if not obj.finished and obj.scheduled_date and obj.scheduled_time:
                mother_filter_changelist_url = get_url_query(1)
                return HttpResponseRedirect(mother_filter_changelist_url)

        return res
