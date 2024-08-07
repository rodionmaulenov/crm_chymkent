from typing import Dict, Any, Optional
from mothers.admin import MotherAdmin
from mothers.filters.short_plan import NewEventOccursFilter, UsersObjectsFilter, IsNewFilter
from mothers.inlines import ScheduledEventInline
from mothers.models.mother import Mother, ScheduledEvent, ShortPlan
from django.contrib import admin
from guardian.shortcuts import get_objects_for_user
from django.contrib.admin.helpers import AdminForm
from mothers.filters.applications import convert_utc_to_local
from django.utils.html import format_html
from django.urls import reverse, path
import pytz
from mothers.services.short_plan import get_mothers_with_recent_incomplete_events
from django.http import JsonResponse
from django.shortcuts import redirect
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@admin.register(ShortPlan)
class ShortPlanAdmin(admin.ModelAdmin):
    list_per_page = 10
    search_help_text = (
        "The IS_NEW field indicates new instances if they have one uncompleted associated scheduled event,"
        "if the number of these associated events is greater than one, it is an old questionnaires.")
    ordering = '-created',
    search_fields = 'name__icontains',
    inlines = [ScheduledEventInline]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    'name', 'age', 'residence', 'height', 'weight', 'caesarean', 'blood', 'children', 'maried'
                ],
            },
        ),
    ]
    list_display = 'name', 'scheduled_event', 'date_create', 'is_new'
    list_filter = [NewEventOccursFilter, UsersObjectsFilter, IsNewFilter]

    class Media:
        css = {
            'all': ('short_plan/css/button_is_completed.css', 'short_plan/css/timezonewarning_remove.css')
        }
        js = ('short_plan/js/redirect_on_add_change_event_tab.js', 'short_plan/js/hide_p_elements.js',
              'short_plan/js/save_scheduled_events.js',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = None

    def get_list_display(self, request):
        if request.GET.get('an_event_occurred') == 'new_event':
            return ['name', 'custom_note', 'is_new_checkbox', 'is_new']
        return super().get_list_display(request)

    def get_list_filter(self, request):
        user_permission = request.user.user_permissions
        if not self.get_queryset(request).exists():
            return []
        if (all(perm.codename.startswith('view') for perm in user_permission.all())
                and user_permission.filter(codename='view_shortplan').exists()):
            return [UsersObjectsFilter, IsNewFilter]
        return [IsNewFilter, NewEventOccursFilter]

    def has_module_permission(self, request) -> bool:

        if not request.user.is_authenticated:
            return False

        view_shortplan = super().has_module_permission(request)

        queryset = get_mothers_with_recent_incomplete_events(Mother.objects.all())

        mother_admin = MotherAdmin(Mother, admin.site)
        mother_model_name = mother_admin.opts.model_name
        custom_permission_name = f'{mother_model_name}_{request.user.username}'.lower()
        klass = mother_admin.opts.model

        users_objs = get_objects_for_user(request.user, perms=custom_permission_name, klass=klass)
        users_objs = get_mothers_with_recent_incomplete_events(users_objs)

        return bool(users_objs) or (view_shortplan and queryset)

    def get_queryset(self, request):

        self.request = request

        queryset = get_mothers_with_recent_incomplete_events(Mother.objects.all())

        mother_admin = MotherAdmin(Mother, admin.site)
        mother_model_name = mother_admin.opts.model_name
        custom_permission_name = f'{mother_model_name}_{request.user.username}'.lower()
        klass = mother_admin.opts.model
        user_permission = request.user.user_permissions

        users_objs = get_objects_for_user(request.user, perms=custom_permission_name, klass=klass)
        filtered_users_objs = get_mothers_with_recent_incomplete_events(users_objs)

        all_perms_is_view = (all(perm.codename.startswith('view') for perm in user_permission.all())
                             and user_permission.filter(codename='view_shortplan').exists())

        if all_perms_is_view:
            return queryset

        else:
            # return users_objs
            return filtered_users_objs

    @admin.display(description='Creation Date')
    def date_create(self, obj):
        local_datetime = convert_utc_to_local(self.request, obj.created)
        return format_html(
            "{} {}, {} {}",
            local_datetime.strftime("%A"),
            local_datetime.strftime("%H:%M"),
            local_datetime.strftime("%d"),
            local_datetime.strftime("%B")
        )

    @admin.display(description='Scheduled event')
    def scheduled_event(self, mother_instance: Mother) -> str:
        # Construct the URL for the admin change page
        url = reverse('admin:mothers_shortplan_change', args=(mother_instance.pk,))

        # Copy filters from the request and add custom parameters
        filters = {key: value for key, value in self.request.GET.items()}
        # Determine event type
        filters['add_or_change'] = 'change'

        # Construct the query string
        query_string = '&'.join([f'{key}={value}' for key, value in filters.items()])

        # Construct the final URL with query parameters
        full_url = f'{url}?{query_string}'

        user_permission = self.request.user.user_permissions
        # Return the HTML link
        if (all(perm.codename.startswith('view') for perm in user_permission.all())
                and user_permission.filter(codename='view_shortplan').exists()):
            return format_html('change event')
        return format_html('<a href="{}">change event</a>', full_url)

    def render_change_form(self, request, context: Dict[str, Any],
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

        if add or change:
            context['show_save_and_add_another'] = False  # Remove "Save and add another" button
            context['show_save_and_continue'] = False  # Remove "Save and continue editing" button
            context['show_save'] = True  # Ensure "Save" button is visible

        return super().render_change_form(request, context, add=add, change=change,
                                          form_url=form_url, obj=obj)

    def save_related(self, request, form, formsets, change):
        """
            Save related objects (inlines), converting scheduled time to UTC for ScheduledEvent instances.
        """
        for formset in formsets:
            formset.save(commit=False)
            for form in formset.forms:
                if form.is_valid():
                    instance = form.save(commit=False)
                    if isinstance(instance, ScheduledEvent):
                        # Example: Convert the scheduled time to UTC before saving
                        utc_time = instance.scheduled_time.astimezone(pytz.utc)
                        instance.scheduled_time = utc_time

                        instance.save()
                    form.save_m2m()
            formset.save_m2m()

        super().save_related(request, form, formsets, change)

    @admin.display(description='Is new?', boolean=True)
    def is_new(self, obj):
        is_new = obj.scheduled_event.count() == 1
        return is_new

    @admin.display(description='Note')
    def custom_note(self, obj):
        return obj.scheduled_event.filter(is_completed=False).first().note

    @admin.display(description='Complete')
    def is_new_checkbox(self, mother_instance):
        checkbox_html = format_html(
            '<input type="checkbox" class="is-new-checkbox" data-mother-id="{}">',
            mother_instance.pk,
        )
        return checkbox_html

    def changelist_view(self, request, extra_context=None):

        queryset = self.get_queryset(request)

        if not queryset.exists():
            return redirect(reverse('admin:index'))

        extra_context = extra_context or {}
        extra_context['show_update_button'] = request.GET.get('an_event_occurred') == 'new_event'
        extra_context['update_url'] = reverse('admin:update_scheduled_events')

        instance_count = queryset.count()

        # Add model name and instance count to context
        extra_context['model_name'] = self.model._meta.verbose_name_plural
        extra_context['instance_count'] = instance_count
        return super().changelist_view(request, extra_context=extra_context)

    @method_decorator(csrf_exempt)
    def update_scheduled_events(self, request):
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                mother_ids = data.get('mother_ids', [])
                for mother_id in mother_ids:
                    mother_instance = Mother.objects.get(pk=mother_id)
                    scheduled_event = ScheduledEvent.objects.filter(mother=mother_instance, is_completed=False).first()
                    if scheduled_event:
                        scheduled_event.is_completed = not scheduled_event.is_completed
                        scheduled_event.save()
                return JsonResponse({'status': 'success'})
            except json.JSONDecodeError as e:
                return JsonResponse({'status': 'failed', 'error': 'Invalid JSON'}, status=400)
            except Exception as e:
                return JsonResponse({'status': 'failed', 'error': str(e)}, status=500)
        return JsonResponse({'status': 'failed', 'error': 'Invalid request method'}, status=400)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('update_scheduled_events/', self.admin_site.admin_view(self.update_scheduled_events),
                 name='update_scheduled_events'),
        ]
        return custom_urls + urls
