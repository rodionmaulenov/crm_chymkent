from typing import Any, Dict, Optional, Tuple, Union

from rangefilter.filters import DateRangeFilter

from django.contrib.admin.helpers import AdminForm
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.db.models import QuerySet
from django.db import models
from django.contrib import admin, messages

from mothers.filters import BoardFilter, ActionFilter
from mothers.inlines import StateInline, PlannedInline, BanInline
from mothers.models import Mother
from mothers.services.mother_classes.command_interface import MoveToBanCommand, ScheduledDateTimeCommand, \
    WhenCreatedCommand
from mothers.services.mother_classes.formatter_interface import BoldDayMonthYearHourMinuteFormatter, \
    DayMonthHourMinuteFormatter
from mothers.services.mother_classes.permissions import PermissionCheckerFactory
from mothers.services.state import adjust_button_visibility
from mothers.services.mother import on_primary_stage, get_model_objects, convert_to_local_time, convert_utc_to_local, \
    tuple_inlines, redirect_to, check_cond

# Globally disable delete selected
admin.site.disable_action('delete_selected')

ContentType: models


@admin.register(Mother)
class MotherAdmin(admin.ModelAdmin):
    list_per_page = 10
    search_help_text = 'Search description'
    ordering = ('-created',)
    inlines = (PlannedInline, StateInline, BanInline)
    list_filter = (
        ('created', DateRangeFilter),
        ActionFilter, BoardFilter,
    )
    list_display_links = ('name',)
    search_fields = ('name__icontains', 'number__icontains', 'program__icontains', 'residence__icontains',
                     'state__reason__icontains')
    fieldsets = [
        (
            None,
            {
                "fields": [
                    'name', 'age', 'number'
                ],

                'description': 'Client personal data',
            },
        ),
        (
            "The rest of data",
            {
                "classes": ["collapse"],
                "fields": [
                    'program', 'blood', 'maried', 'citizenship', 'residence', 'height_and_weight', 'caesarean',
                    'children_age', 'bad_habits'
                ],
            },
        ),

    ]
    list_display = (
        'id', 'when_created', 'name', 'number', 'age', 'blood', 'create_plan', 'create_state'
    )

    actions = ['move_to_ban']

    def get_inlines(self, request, obj):
        inlines = super().get_inlines(request, obj)
        return tuple_inlines(obj, inlines)

    def get_list_display(self, request: HttpRequest) -> Tuple[str, ...]:
        """
        Display another tuple of fields depends on filtered queryset
        """
        if request.GET.get('filter_set') == 'scheduled_event':
            return ('id', 'name', 'number', 'age', 'blood',
                    'create_state', 'state_datetime', 'reason')

        if request.GET.get('actions') == 'state_actions':
            return ('id', 'name', 'number', 'age', 'blood',
                    'create_state', 'reason', 'state_datetime')

        if request.GET.get('actions') == 'planned_actions':
            return ('id', 'name', 'number', 'age', 'blood',
                    'create_plan')

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
        Redirect on filtered or without filters change list page.
        """
        text = 'Successfully changed'
        path_dict = {
            'message_url': reverse('admin:mothers_mother_change', args=[obj.pk]),
            'base_url': reverse('admin:mothers_mother_changelist')
        }

        return redirect_to(request, obj, text, path_dict, messages.SUCCESS)

    def has_module_permission(self, request: HttpRequest) -> bool:
        """
        A user with basic permission or assigned objs permission.
        """
        base = super().has_module_permission(request)
        class_name = 'ModulePermission'
        permission_checker = PermissionCheckerFactory.get_checker(self, request, class_name)
        has_perm = permission_checker.has_permission(base, on_primary_stage)
        return has_perm

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """
        Queryset contains exclusively the Mother instances where Stage is Primary.
        """
        queryset = super().get_queryset(request)
        # assign request for using in custom MotherAdmin methods
        self.request = request
        user = request.user

        prefetch_query = queryset.prefetch_related(
            'state_set', 'planned_set', 'ban_set', 'stage_set'
        )

        if user.has_module_perms(self.opts.app_label):
            queryset = on_primary_stage(prefetch_query)
            return queryset

        data = get_model_objects(self, request)
        users_mothers = on_primary_stage(data)
        return users_mothers

    def has_view_permission(self, request: HttpRequest, mother: Mother = None) -> bool:
        class_name = 'ObjectListLevelPermission'
        permission_checker = PermissionCheckerFactory.get_checker(self, request, class_name)
        has_perm = permission_checker.has_permission('view', on_primary_stage, obj=mother)
        return has_perm

    def has_change_permission(self, request: HttpRequest, mother: Mother = None) -> bool:
        class_name = 'BasedOnUrlChangePermission'
        permission_checker = PermissionCheckerFactory.get_checker(self, request, class_name)
        has_perm = permission_checker.has_permission('change', on_primary_stage, obj=mother)
        return has_perm

    @admin.display(description='created')
    def when_created(self, obj: Mother) -> str:
        """
        Converts the UTC creation date to the user's local time.
        """
        date_creation = WhenCreatedCommand(self.request, obj)
        return date_creation.execute()

    @admin.display(description='extra reason')
    def reason(self, obj: Mother) -> str:
        return obj.state.first().reason

    @admin.display(description='state')
    def create_state(self, mother: Mother) -> Union[str, None]:
        """
        Generate links for different states:
          First, if the state exists, the URL for changing is generated;
          Second, if another related instance already exists, nothing is returned;
          Third, returns the URL for adding if no instances exist.
        """
        return check_cond(self.request, mother, 'state')

    @admin.display(description='scheduled date/time')
    def state_datetime(self, mother: Mother) -> Union[str, None]:
        """
        Show scheduled time for mother state.
        """
        planed_date = ScheduledDateTimeCommand(self.request, mother)
        return planed_date.execute()

    @admin.display(description='plan')
    def create_plan(self, mother: Mother) -> Union[str, None]:
        """
        Prepares client for sending into laboratory.

        Generate links for different states:
          First, if the plan exists, the URL for changing is generated;
          Second, if another related instance already exists, nothing is returned;
          Third, returns the URL for adding if no instances exist.
        """
        return check_cond(self.request, mother, 'planned')

    @admin.action(description='move to ban')
    def move_to_ban(self, request, queryset):
        send_to_ban = MoveToBanCommand(request, queryset)
        return send_to_ban.execute()
