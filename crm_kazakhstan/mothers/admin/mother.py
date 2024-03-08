from typing import Any, Dict, Optional, Tuple
from rangefilter.filters import DateRangeFilter

from django.contrib.admin.helpers import AdminForm
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import QuerySet, F
from django.utils.translation import ngettext
from django.db import transaction
from django.contrib import admin, messages

from mothers.filters import BoardFilter, BanFilter
from mothers.inlines import StateInline, PlannedInline, BanInline
from mothers.models import Mother, Stage
from mothers.services.state import filtered_mothers, filters_datetime, adjust_button_visibility, render_icon
from mothers.services.mother import on_primary_stage, has_permission, get_model_objects, output_time_format, \
    convert_to_local_time, add_new, simple_text, reduce_text, extract_from_url, change, can_not_change_on_changelist, \
    FromUrlSpec, BaseFilter, convert_utc_to_local, after_change_message, tuple_inlines

# Globally disable delete selected
admin.site.disable_action('delete_selected')


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
        BoardFilter, BanFilter
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
        'id', 'when_created', 'name', 'number', 'age', 'blood', 'create_ban', 'create_condition_link', 'reason',
        'create_condition_datetime')

    actions = ["move_to_ban"]

    def get_inlines(self, request, obj):
        inlines = super().get_inlines(request, obj)
        return tuple_inlines(obj, inlines)

    def get_list_display(self, request: HttpRequest) -> Tuple[str, ...]:
        """
        Display another tuple of fields depends on filtered queryset
        """
        if request.GET.get('filter_set') == 'scheduled_event':
            return ('id', 'name', 'number', 'age', 'blood',
                    'create_condition_link', 'reason', 'create_condition_datetime')

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
        if super().has_module_permission(request):
            return True

        data = get_model_objects(self, request, ['primary_stage'])
        users_mothers = on_primary_stage(data).exists()
        return users_mothers

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """
        Queryset contains exclusively the Mother instances where Stage is Primary.
        """
        # assign request for using in custom MotherAdmin methods
        self.request = request

        queryset = super().get_queryset(request)
        prefetch_query = queryset.prefetch_related(
            'state_set', 'planned_set', 'ban_set', 'stage_set'
        )
        queryset = on_primary_stage(prefetch_query)

        if request.user.has_perm('mothers.view_mother'):
            return queryset

        data = get_model_objects(self, request, ['primary_stage'])
        users_mothers = on_primary_stage(data)
        return users_mothers

    def has_view_permission(self, request: HttpRequest, obj: Mother = None) -> bool:
        return has_permission(self, request, obj, 'view')

    def has_change_permission(self, request: HttpRequest, obj: Mother = None) -> bool:
        mother_changelist = reverse('admin:mothers_mother_changelist')
        if mother_changelist in request.get_full_path():
            return has_permission(self, request, obj, 'change')
        return request.user.is_superuser

    @admin.display(description='created', empty_value="no date", )
    def when_created(self, obj: Mother) -> str:
        """
        Returns the creation date of the Mother instance, converted from UTC to the user's local timezone.
        """
        user_timezone = getattr(self.request.user, 'timezone', 'UTC')

        local_time = convert_to_local_time(obj, user_timezone)
        return output_time_format(local_time)

    @admin.display(description='reason')
    def reason(self, obj: Mother) -> str:
        return obj.state_set.last().reason

    @admin.display(description='state')
    def create_condition_link(self, obj: Mother) -> format_html:
        """
        Generate links or simple text for different states
        """
        request = self.request
        state = obj.last_state
        plan = obj.plan
        ban = obj.ban
        params = extract_from_url(request, 'filter_set', 'scheduled_event')
        state_obj = obj.state_set.last()
        text = reduce_text(state_obj)

        filters = filters_datetime(obj)
        filtered_page = filtered_mothers(filters)

        if not state and (plan or ban):
            return simple_text(text)
        if not state and not plan and not ban:
            path = reverse('admin:mothers_state_add')
            return add_new(obj, text, path)
        if state and not params and not filtered_page:
            return change(state_obj, text)
        if state and not params and filtered_page:
            return can_not_change_on_changelist(text)
        if state and params and filtered_page:
            return change(state_obj, text)

    @admin.display(description='planned event')
    def create_condition_datetime(self, obj: Mother) -> str:
        """
        Show planned time.
        """
        request = self.request
        state = obj.state_set.last()
        from_filtered = extract_from_url(request, 'planned_time', 'datetime')

        filters = filters_datetime(obj)
        on_filtered_page = filtered_mothers(filters)

        formatted_datetime = None
        if not state.finished:
            local_time = convert_utc_to_local(request, state.scheduled_date, state.scheduled_time)
            formatted_datetime = output_time_format(local_time)

        if not from_filtered and not state.finished and not on_filtered_page:
            return formatted_datetime
        if not from_filtered and not state.finished and on_filtered_page:
            return formatted_datetime
        if from_filtered and not state.finished and on_filtered_page:
            return formatted_datetime

    @admin.display(description='ban')
    def create_ban(self, obj: Mother) -> str:
        """
        Prepare instance to pass into ban.
        """
        state = obj.last_state
        plan = obj.plan
        ban = obj.ban

        if (state or plan) and not ban:
            # one instance from two exists
            return '-'
        elif not ban and not state and not plan:
            # none exists
            path = reverse('admin:mothers_ban_add')
            text = '<strong>to ban</strong>'
            return add_new(obj, text, path)
        elif ban and not state and not plan:
            # only ban exists
            return render_icon(is_success=False)

    @admin.action(description='move to ban')
    def move_to_ban(self, request, queryset):
        mothers = queryset.filter(ban__banned=False)

        with transaction.atomic():
            # Bulk create new stages for each mother
            new_stages = [Stage(mother=mother, stage=Stage.StageChoices.BAN) for mother in mothers]
            Stage.objects.bulk_create(new_stages)

            # Update the previous stages for each mother to be finished
            Stage.objects.filter(
                mother__in=mothers,
                id__lt=F('mother__stage__id'),
                # Ensure we only update stages with IDs less than the newly created stages
                finished=False
            ).update(finished=True)

            mothers = len(mothers)
            self.message_user(
                request,
                ngettext(
                    "%d mother was successfully transferred to the ban.",
                    "%d mothers were successfully transferred to the ban.",
                    mothers,
                )
                % mothers,
                messages.SUCCESS,
            )
