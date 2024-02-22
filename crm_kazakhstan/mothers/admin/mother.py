from typing import Any, Dict, Optional, Tuple, List
from rangefilter.filters import DateRangeFilter

from django.contrib.admin.helpers import AdminForm
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import QuerySet
from django.contrib import admin

from mothers.filters import PlannedTimeFilter, CreatedStatusFilter, EmptyConditionFilter, DateFilter, \
    ConditionDateFilter
from mothers.inlines import ConditionInline, CommentInline, PlannedInline
from mothers.models import Mother
from mothers.services.condition import filtered_mothers, filters_datetime, adjust_button_visibility
from mothers.services.mother import on_primary_stage, has_permission, get_model_objects, output_time_format, \
    convert_to_local_time, add_new, simple_text, bold_text, extract_from_url, can_change_on_changelist, \
    can_not_change_on_changelist, change_on_filtered_changelist, FromUrlSpec, BaseFilter, date_time_or_exception, \
    convert_utc_to_local

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
        DateFilter, PlannedTimeFilter, CreatedStatusFilter, EmptyConditionFilter
    )
    list_display_links = ('name',)
    search_fields = ('name__icontains', 'number__icontains', 'program__icontains', 'residence__icontains',)
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
    list_display = ('id', 'when_created', 'name', 'number', 'age', 'blood', 'create_condition_link',
                    'create_condition_datetime')

    def get_search_fields(self, request):
        pass

    def get_search_results(self, request, queryset, search_term):
        pass

    def get_ordering(self, request: HttpRequest) -> List[str]:
        """
        Return list of fields ordered in specific way
        """

        created_condition = ["-condition__created"]

        if request.GET.get('planned_time'):
            return created_condition
        elif request.GET.get('empty_state'):
            return created_condition
        else:
            return super().get_ordering(request)

    def lookup_allowed(self, lookup: str, value: Any) -> bool:
        """
        Check if a lookup is allowed based on specific conditions.
        """

        if lookup == 'planned_time':
            date_time_or_exception()

        return super().lookup_allowed(lookup, value)

    def get_list_filter(self, request: HttpRequest):
        """
        Based on request return certain filters
        """
        if request.GET.get('recently_created'):
            return DateFilter, CreatedStatusFilter
        elif request.GET.get('planned_time'):
            return ConditionDateFilter, PlannedTimeFilter
        elif request.GET.get('empty_state'):
            return ConditionDateFilter, EmptyConditionFilter

        return super().get_list_filter(request)

    def get_list_display(self, request: HttpRequest) -> Tuple[str, ...]:
        """
        Display another tuple of fields depends on filtered queryset
        """
        if request.GET.get('planned_time'):
            return ('id', 'name', 'number', 'age', 'blood', 'reason',
                    'create_condition_link', 'create_condition_datetime')
        elif request.GET.get('empty_state'):
            return ('id', 'name', 'number', 'age', 'blood', 'reason',
                    'create_condition_link', 'create_condition_datetime')
        elif request.GET.get('recently_created'):
            return ('id', 'name', 'number', 'age', 'blood', 'reason',
                    'create_condition_link')

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
        After change redirect on previous url if exists or on changelist
        """

        mother_changelist = reverse('admin:mothers_mother_changelist')

        changelist_spec = FromUrlSpec('_changelist_filters')
        changelist = BaseFilter()
        changelist_param = changelist.filter(request.GET, changelist_spec)

        if changelist_param:
            return HttpResponseRedirect(mother_changelist + '?' + changelist_param)
        return HttpResponseRedirect(mother_changelist)

    def has_module_permission(self, request: HttpRequest) -> bool:
        """
        Permission for first layer on site, see or not Mother. If superuser True else objects that has the same
        with user perms exist or not.
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
        prefetch_query = queryset.prefetch_related(
            'condition_set', 'planned_set', 'comment_set', 'stage_set'
        )
        queryset = on_primary_stage(prefetch_query)

        if request.user.has_perm('mothers.view_mother'):
            return queryset

        data = get_model_objects(self, request)
        data = on_primary_stage(data)
        return data

    def has_view_permission(self, request: HttpRequest, obj: Mother = None) -> bool:
        return has_permission(self, request, obj, 'view')

    def has_change_permission(self, request: HttpRequest, obj: Mother = None) -> bool:
        return has_permission(self, request, obj, 'change')

    @admin.display(description='created', empty_value="no date", )
    def when_created(self, obj: Mother) -> str:
        """
        Returns the creation date of the Mother instance, converted from UTC to the user's local timezone.
        """
        user_timezone = getattr(self.request.user, 'timezone', 'UTC')

        local_time = convert_to_local_time(obj, user_timezone)
        return output_time_format(local_time)

    @admin.display(description='reason', empty_value="no reason")
    def reason(self, obj: Mother) -> str:
        return obj.last_condition.reason

    @admin.display(description='status', empty_value='no status')
    def create_condition_link(self, obj: Mother) -> format_html:
        """
        Generate links or simple text for different states
        """
        request = self.request
        condition = obj.last_condition
        planned = obj.last_planned
        comment = obj.last_comment
        from_filtered = extract_from_url(request, 'planned_time', 'datetime')
        text = bold_text(condition)

        filters = filters_datetime(obj)
        on_filtered_page = filtered_mothers(filters)

        if condition.finished and (planned or comment):
            return simple_text(text)
        if condition.finished and not (planned or comment):
            return add_new(obj, text, request)
        if not from_filtered and not condition.finished and not on_filtered_page:
            return can_change_on_changelist(condition, text)
        if not from_filtered and not condition.finished and on_filtered_page:
            return can_not_change_on_changelist(text)
        if from_filtered and not condition.finished and on_filtered_page:
            return change_on_filtered_changelist(condition, text)

    @admin.display(description='planned time', empty_value="")
    def create_condition_datetime(self, obj: Mother) -> str:
        request = self.request
        condition = obj.last_condition
        from_filtered = extract_from_url(request, 'planned_time', 'datetime')

        filters = filters_datetime(obj)
        on_filtered_page = filtered_mothers(filters)

        formatted_datetime = None
        if not condition.finished:
            local_time = convert_utc_to_local(request, condition.scheduled_date, condition.scheduled_time)
            formatted_datetime = output_time_format(local_time)

        if not from_filtered and not condition.finished and not on_filtered_page:
            return formatted_datetime
        if not from_filtered and not condition.finished and on_filtered_page:
            return formatted_datetime
        if from_filtered and not condition.finished and on_filtered_page:
            return formatted_datetime
