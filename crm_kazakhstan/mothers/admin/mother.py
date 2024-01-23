from typing import Any, Dict, Optional
from dateutil import parser

from django.contrib.admin.helpers import AdminForm
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import QuerySet
from django.contrib import admin

from mothers.filters import AuthConditionListFilter
from mothers.inlines import ConditionInline, CommentInline, PlannedInline
from mothers.models import Mother
from mothers.services.condition import queryset_with_filter_condition, filter_condition_by_date_time, \
    is_filtered_condition_met, redirect_to_appropriate_url, adjust_button_visibility
from mothers.services.mother import (aware_datetime_from_date, on_primary_stage, determine_link_action,
                                     has_permission, get_model_objects, output_time_format, convert_to_local_time,
                                     check_datetime_lookup_permission)

# Globally disable delete selected
admin.site.disable_action('delete_selected')


@admin.register(Mother)
class MotherAdmin(admin.ModelAdmin):
    empty_value_display = "-empty-"
    ordering = ('-date_create',)
    inlines = (PlannedInline, ConditionInline, CommentInline,)
    list_filter = ("date_create", AuthConditionListFilter)
    list_display = (
        'id', 'name', 'date_created', 'number', 'residence', 'height_and_weight',
        'bad_habits', 'caesarean', 'children_age', 'age', 'citizenship', 'blood', 'maried',
        "create_condition_link",
    )

    actions = ('first_visit_stage', 'delete_selected', 'banned')

    list_display_links = ('name', 'residence',)
    readonly_fields = ('date_created',)
    search_fields = ('number', 'program', 'residence__icontains',)
    view_on_site = False
    fieldsets = [
        (
            None,
            {
                "fields": [(
                    'name', 'number', 'program', 'residence', 'height_and_weight', 'date_created',
                    'bad_habits', 'caesarean', 'children_age', 'age', 'citizenship', 'blood', 'maried'
                ), ],

                'description': 'Client personal data',
            },
        )
    ]

    search_help_text = 'Search description'

    def lookup_allowed(self, lookup: str, value: Any) -> bool:
        """
        Check if a lookup is allowed based on specific conditions.
        """
        if lookup == 'date_or_time':
            check_datetime_lookup_permission()

        return super().lookup_allowed(lookup, value)

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

    def get_search_results(self, request, queryset, search_term):
        """
        User has possibility search instances from includes date input to date.today()
        """
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        try:
            if search_term[:4].isdigit():
                search_date = parser.parse(search_term).date()
                aware_datetime = aware_datetime_from_date(search_date)
            else:
                search_date = parser.parse(search_term, dayfirst=True).date()
                aware_datetime = aware_datetime_from_date(search_date)

            queryset |= self.model.objects.filter(date_create__gte=aware_datetime)
        except parser.ParserError:
            pass

        return queryset, use_distinct

    @admin.display(empty_value="no date", description='date created')
    def date_created(self, obj: Mother) -> str:
        """
        Returns the creation date of the Mother instance, converted from UTC to the user's local timezone.
        """
        user_timezone = getattr(self.request.user, 'timezone', 'UTC')

        # Convert the 'date_create' of the Mother instance to the user's local time
        local_time = convert_to_local_time(obj, user_timezone)
        # Format the local time and return it
        return output_time_format(local_time)

    @admin.display(description='Status/Time')
    def create_condition_link(self, obj: Mother) -> format_html:
        """
        Determine the appropriate action for the condition link based on the condition of the 'Mother' object.
        """

        return determine_link_action(self.request, obj)
