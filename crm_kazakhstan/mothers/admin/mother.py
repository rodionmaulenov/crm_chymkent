from typing import Any, Dict, Optional, Tuple
from rangefilter.filters import DateRangeFilter

from django.contrib.admin.helpers import AdminForm
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import QuerySet
from django.contrib import admin

from mothers.filters import AuthConditionFilter, AuthDateFilter, AuthCreatedStatusFilter
from mothers.inlines import ConditionInline, CommentInline, PlannedInline
from mothers.models import Mother
from mothers.services.condition import queryset_with_filter_condition, filter_condition_by_date_time, \
    is_filtered_condition_met, redirect_to_appropriate_url, adjust_button_visibility
from mothers.services.mother import (on_primary_stage, determine_link_action,
                                     has_permission, get_model_objects, output_time_format, convert_to_local_time,
                                     check_datetime_lookup_permission)

# Globally disable delete selected
admin.site.disable_action('delete_selected')


@admin.register(Mother)
class MotherAdmin(admin.ModelAdmin):
    view_on_site = True
    list_max_show_all = 30
    list_per_page = 20
    empty_value_display = "-empty-"
    search_help_text = 'Search description'
    ordering = ('-date_create',)
    inlines = (PlannedInline, ConditionInline, CommentInline,)
    list_filter = (
        ('date_create', DateRangeFilter),
        AuthDateFilter, AuthConditionFilter, AuthCreatedStatusFilter
    )
    actions = ('first_visit_stage', 'delete_selected', 'banned')

    list_display_links = ('name', 'residence',)
    search_fields = ('number', 'program', 'residence__icontains',)
    fieldsets = [
        (
            None,
            {
                "fields": [
                    'name', 'age', 'number', 'blood', 'maried'
                ],

                'description': 'Client personal data',
            },
        ),
        (
            "The rest of data",
            {
                "classes": ["collapse"],
                "fields": [
                    'program', 'citizenship', 'residence', 'height_and_weight', 'caesarean',
                    'children_age', 'bad_habits'
                ],
            },
        ),

    ]
    list_display = ('id', 'name', 'number', 'age', 'blood', 'height_and_weight', 'maried',
                    'children_age', 'caesarean', 'residence', 'when_created', "create_condition_link")

    def lookup_allowed(self, lookup: str, value: Any) -> bool:
        """
        Check if a lookup is allowed based on specific conditions.
        """
        if lookup == 'date_or_time':
            check_datetime_lookup_permission()

        return super().lookup_allowed(lookup, value)

    def get_list_display(self, request: HttpRequest) -> Tuple[str, ...]:
        """
        Display another tuple of fields when filtered queryset
        """
        if request.GET.get('date_or_time'):
            return 'id', 'name', 'number', 'age', 'blood', 'reason', "create_condition_link"
        return super().get_list_display(request)

    def render_change_form(self, request: HttpRequest, context: Dict[str, Any],
                           add: bool = False, change: bool = False,
                           form_url: str = '', obj: Optional[Mother] = None) -> AdminForm:
        """
        Override the method to modify the context for the change form template.

        This method is called before the admin form is rendered and allows us to
        alter the context dictionary that is passed to the template. The visibility
        of the "Save and add another" and "Save and continue editing" buttons is
        controlled based on whether a new instance is being added or an existing
        instance is being changed.
        """

        adjust_button_visibility(context, add, change)

        return super().render_change_form(request, context, add=add, change=change,
                                          form_url=form_url, obj=obj)

    def response_change(self, request: HttpRequest, obj: Mother) -> HttpResponseRedirect:
        """
        Customizes the response after editing a 'Mother' instance in the admin interface.
        Redirects to the previous URL if available and valid after the condition is changed.
        If no previous URL is set or if the filtered change list is empty, redirects to the Mother change list page.
        """

        for_datetime = filter_condition_by_date_time()
        for_datetime = queryset_with_filter_condition(for_datetime)

        previous_url = request.session.get('previous_url')
        mother_changelist_url = reverse('admin:mothers_mother_changelist')

        # Check if the previous URL corresponds to a filtered condition
        if is_filtered_condition_met(previous_url, for_datetime):
            return redirect_to_appropriate_url(request, previous_url, mother_changelist_url)
        # Redirect to the Mother change list page if no previous URL is set or valid
        return HttpResponseRedirect(mother_changelist_url)

    def has_module_permission(self, request: HttpRequest) -> bool:
        """
        Permission for first layer on site, see or not Mother.
        If superuser True else objects that has the same with user perms exist or not.
        """
        if super().has_module_permission(request):
            return True
        data = on_primary_stage(get_model_objects(self, request))
        return data.exists()

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """
        Queryset contains exclusively the Mother instances where Stage is Primary
        """
        # assign request for using in custom MotherAdmin methods
        self.request = request

        queryset = super().get_queryset(request)
        queryset = on_primary_stage(queryset)

        if request.user.is_superuser:
            return queryset

        data = get_model_objects(self, request)
        data = on_primary_stage(data)
        return data

    def has_view_permission(self, request: HttpRequest, obj: Mother = None) -> bool:
        """
        Checks if the user has the 'view' permission for the given object or model.
        """
        base_permission = super().has_view_permission(request, obj)
        return has_permission(self, request, obj, 'view', base_permission)

    def has_change_permission(self, request: HttpRequest, obj: Mother = None) -> bool:
        """
        Checks if the user has the 'change' permission for the given object or model.
        """
        base_permission = super().has_change_permission(request, obj)
        return has_permission(self, request, obj, 'change', base_permission)

    @admin.display(empty_value="no date", description='when created')
    def when_created(self, obj: Mother) -> str:
        """
        Returns the creation date of the Mother instance, converted from UTC to the user's local timezone.
        """
        user_timezone = getattr(self.request.user, 'timezone', 'UTC')

        # Convert the 'date_create' of the Mother instance to the user's local time
        local_time = convert_to_local_time(obj, user_timezone)
        # Format the local time and return it
        return output_time_format(local_time)

    @admin.display(description='reason')
    def reason(self, obj: Mother) -> str:
        return obj.condition_set.order_by('-id').first().reason

    @admin.display(description='Status/Time')
    def create_condition_link(self, obj: Mother) -> format_html:
        """
        Determine the appropriate action for the condition link based on the condition of the 'Mother' object.
        """

        return determine_link_action(self.request, obj)
