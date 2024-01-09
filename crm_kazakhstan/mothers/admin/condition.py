from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

from mothers.models import Condition


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

    def response_change(self, request, obj):
        """
        Overrides the response after editing an existing 'Condition' instance in the admin.
        Redirects back to the 'Mother' admin page with the same filters applied as before if
        the user hasn't chosen to continue editing.
        """
        res = super().response_change(request, obj)
        if '_continue' not in request.POST and '_addanother' not in request.POST:
            return_path = request.GET.get('_changelist_filters')
            if return_path:
                return HttpResponseRedirect(return_path)

        return res

        # if obj.finished:
        #     mother_changelist_url = reverse('admin:mothers_mother_changelist')
        #     return HttpResponseRedirect(mother_changelist_url)