from typing import Any, Dict, Optional, Tuple, Union
from rangefilter.filters import DateRangeFilter

from django.contrib.admin.helpers import AdminForm
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import QuerySet
from django.shortcuts import redirect
from django.db import models
from django.contrib import admin, messages

from mothers.filters import BoardFilter, ActionFilter
from mothers.inlines import StateInline, PlannedInline, BanInline
from mothers.models import Stage, Mother
from mothers.services.mother_classes.command_interface import get_command, get_command2
from mothers.services.mother_classes.formatter_interface import BoldDayMonthYearHourMinuteFormatter, \
    CombinedExtractor, StateExtractor, TextReducer, DayMonthHourMinuteFormatter, PlanExtractor
from mothers.services.state import adjust_button_visibility
from mothers.services.mother import on_primary_stage, has_permission, get_model_objects, convert_to_local_time, \
    change, FromUrlSpec, BaseFilter, convert_utc_to_local, after_change_message, tuple_inlines

# Globally disable delete selected
admin.site.disable_action('delete_selected')

ContentType: models


@admin.register(Mother)
class MotherAdmin(admin.ModelAdmin):
    view_on_site = True
    list_max_show_all = 30
    list_per_page = 20
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
        After change redirect on previous url if exists or on changelist
        """
        self.message_user(request, after_change_message(obj), level=messages.SUCCESS)
        mother_changelist = reverse('admin:mothers_mother_changelist')

        changelist_spec = FromUrlSpec('_changelist_filters')
        changelist = BaseFilter()
        changelist_param = changelist.filter(request.GET, changelist_spec)

        if changelist_param:
            return HttpResponseRedirect(mother_changelist + '?' + changelist_param)
        return HttpResponseRedirect(mother_changelist)

    def has_module_permission(self, request: HttpRequest) -> bool:
        """
        Basic behavior or when user has is assigned him custom ``Permission``- ``app_label.codename``.
        """
        base = super().has_module_permission(request)
        stage = request.user.stage

        data = get_model_objects(self, request, stage)
        users_mothers = on_primary_stage(data).exists()

        return users_mothers or base

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """
        Queryset contains exclusively the Mother instances where Stage is Primary.
        """
        queryset = super().get_queryset(request)
        # assign request for using in custom MotherAdmin methods
        self.request = request
        user = request.user
        stage = user.stage

        prefetch_query = queryset.prefetch_related(
            'state_set', 'planned_set', 'ban_set', 'stage_set'
        )
        queryset = on_primary_stage(prefetch_query)

        if user.has_perm('mothers.view_mother'):
            return queryset

        data = get_model_objects(self, request, stage)
        users_mothers = on_primary_stage(data)
        return users_mothers

    def has_view_permission(self, request: HttpRequest, obj: Mother = None) -> bool:
        return has_permission(self, request, 'view', obj)

    def has_change_permission(self, request: HttpRequest, obj: Mother = None) -> bool:
        changelist = reverse('admin:mothers_mother_changelist')
        if changelist in request.get_full_path():
            return has_permission(self, request, 'change', obj)
        return False

    @admin.display(description='created', empty_value="no date", )
    def when_created(self, obj: Mother) -> str:
        """
        Returns the creation date of the Mother instance, converted from UTC to the user's local timezone.
        """
        user_timezone = getattr(self.request.user, 'timezone', 'UTC')

        local_time = convert_to_local_time(obj, user_timezone)
        formatter = DayMonthHourMinuteFormatter()
        formatting = formatter.format(local_time)
        return formatting

    @admin.display(description='extra reason', empty_value='')
    def reason(self, obj: Mother) -> str:
        return obj.state.first().reason

    @admin.display(description='state', empty_value='')
    def create_state(self, mother: Mother) -> format_html:
        """
        Generate links for different states.
        """
        change_url = 'admin:mothers_state_change'
        add_url = 'admin:mothers_state_add'

        state = mother.state.exists()
        plan = mother.plan.exists()
        ban = mother.ban.exists()

        state_instance = None
        text = None
        if state:
            state_instance = mother.state.first()
            extractor = CombinedExtractor(StateExtractor())
            cutter = TextReducer(extractor)
            text = cutter.reduce_text(state_instance)

        command = get_command(state, plan, ban)
        result = command.execute(change_url=change_url, add_url=add_url, mother=mother, obj=state_instance, text=text)
        return result

    @admin.display(description='timetable state', empty_value='')
    def state_datetime(self, mother: Mother) -> Union[str, None]:
        """
        Show timetable for state.
        """
        request = self.request
        state = mother.state.exists()

        formatting = None
        if state:
            state_instance = mother.state.first()
            to_local = convert_utc_to_local(request, state_instance.scheduled_date, state_instance.scheduled_time)

            formatter = BoldDayMonthYearHourMinuteFormatter()
            formatting = formatter.format(to_local)

        return formatting

    @admin.display(description='plan', empty_value='')
    def create_plan(self, mother: Mother) -> str:
        """
        Prepares client for sending into laboratory.
        """
        change_url = 'admin:mothers_planned_change'
        add_url = 'admin:mothers_planned_add'

        state = mother.state.exists()
        plan = mother.plan.exists()
        ban = mother.ban.exists()

        plan_instance = None
        text = None
        if plan:
            plan_instance = mother.plan.first()
            extractor = CombinedExtractor(PlanExtractor())
            cutter = TextReducer(extractor)
            text = cutter.reduce_text(plan_instance)

        command = get_command2(state, plan, ban)
        result = command.execute(change_url=change_url, add_url=add_url, mother=mother, obj=plan_instance, text=text)
        return result

    @admin.action(description='move to ban')
    def move_to_ban(self, request, queryset):

        mothers = queryset.count()
        if mothers == 1:
            mother = queryset.first()
            add_url = reverse('admin:mothers_ban_add')
            # Add the mother's ID as a query parameter
            add_url_with_mother_id = f"{add_url}?mother={mother.pk}"
            return redirect(add_url_with_mother_id)
        else:
            self.message_user(
                request,
                format_html('Please choose only one instance'),
                messages.ERROR,
            )
