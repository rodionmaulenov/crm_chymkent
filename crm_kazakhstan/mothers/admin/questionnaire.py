from typing import Dict, Any, Optional
from mothers.admin import MotherAdmin
from mothers.filters.questionnaire import UsersObjectsFilter, IsNewFilter
from mothers.inlines import ScheduledEventInline
from mothers.models.mother import Questionnaire, Mother, ScheduledEvent
from django.contrib import admin
from guardian.shortcuts import get_objects_for_user
from django.contrib.admin.helpers import AdminForm
from mothers.filters.applications import convert_utc_to_local
from django.utils.html import format_html
from django.urls import reverse
import pytz

from mothers.services.questionnaire import get_mothers_without_incomplete_event


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_per_page = 10
    search_help_text = ("IS_NEW field shows new instances if they have no associated scheduled events,"
                        " otherwise they are old questionnaires.")
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
    list_display = 'name', 'mass_index', 'scheduled_event', 'add_laboratory_link', 'date_create', 'is_new'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = None

    class Media:
        css = {
            'all': ('questionnaire/css/timezonewarning_remove.css',)
        }

        js = 'questionnaire/js/redirect_on_add_change_event_tab.js', 'questionnaire/js/hide_p_elements.js',

    def get_list_filter(self, request):
        user_permission = request.user.user_permissions
        if not self.get_queryset(request).exists():
            return []
        if (all(perm.codename.startswith('view') for perm in user_permission.all())
                and user_permission.filter(codename='view_questionnaire').exists()):
            return [UsersObjectsFilter, IsNewFilter]
        return [IsNewFilter]

    def get_inlines(self, request, obj):
        # When an inline has one or more instances and then return these inlines
        # Cases when read
        if request.GET.get('add_or_change', False):
            return super().get_inlines(request, obj)
        else:
            inlines = super().get_inlines(request, obj)
            filtered_inlines = [
                inline for inline in inlines
                if inline.model.objects.filter(mother=obj).exists()
            ]
            return filtered_inlines

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request) -> bool:
        """
            Determines if the user has permission to access the module.

            1. Checks if the user is authenticated. If not, returns False.
            2. Filters the queryset to include instances where certain fields (age, residence, height, weight,
            caesarean, children) are not null.
            3. Excludes instances where related ScheduledEvent instances have `is_completed=False`.
            4. Returns True if the user has custom permissions for any objects or the 'view_questionnaire'
            permission along with the filtered queryset.
        """
        if not request.user.is_authenticated:
            return False

        view_questionnaire = super().has_module_permission(request)

        queryset = get_mothers_without_incomplete_event(Mother.objects.all())

        mother_admin = MotherAdmin(Mother, admin.site)
        mother_model_name = mother_admin.opts.model_name
        custom_permission_name = f'{mother_model_name}_{request.user.username}'.lower()
        klass = mother_admin.opts.model

        users_objs = get_objects_for_user(request.user, perms=custom_permission_name, klass=klass)
        users_objs = get_mothers_without_incomplete_event(users_objs)

        return bool(users_objs) or (view_questionnaire and queryset)

    def get_queryset(self, request):
        """
            Customizes the queryset for the Mother model based on specific conditions:

            1. Filters the queryset to include instances where certain fields (age, residence, height,
               weight, caesarean, children) are not null.
            2. Excludes instances where related ScheduledEvent instances have `is_completed=False`.
            3. Checks if the user has a custom permission and filters the queryset further based on this permission.
            4. If the user has all permissions starting with 'view' and specifically the 'view_questionnaire' permission,
               returns the initially filtered queryset.
            5. Otherwise, returns the queryset filtered by both the custom permission and non-null fields.
        """
        self.request = request

        queryset = get_mothers_without_incomplete_event(Mother.objects.all())

        mother_admin = MotherAdmin(Mother, admin.site)
        mother_model_name = mother_admin.opts.model_name
        custom_permission_name = f'{mother_model_name}_{request.user.username}'.lower()
        klass = mother_admin.opts.model
        user_permission = request.user.user_permissions

        users_objs = get_objects_for_user(request.user, perms=custom_permission_name, klass=klass)
        users_objs = get_mothers_without_incomplete_event(users_objs)

        if (all(perm.codename.startswith('view') for perm in user_permission.all())
                and user_permission.filter(codename='view_questionnaire').exists()):
            return queryset

        return users_objs

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

    @staticmethod
    def classify_bmi(bmi):
        if bmi < 18.5:
            return "Underweight (less than 18.5) - Low"
        elif 18.5 <= bmi < 25:
            return "Normal weight (18.5-24.9) - Normal"
        elif 25 <= bmi < 30:
            return "Overweight (pre-obesity) (25.0-29.9) - Increased"
        elif 30 <= bmi < 35:
            return "Obesity Class I (30.0-34.9) - High"
        elif 35 <= bmi < 40:
            return "Obesity Class II (35.0-39.9) - Very High"
        else:
            return "Obesity Class III (40.0 and above) - Extremely High"

    @admin.display(description='Mass index')
    def mass_index(self, obj):
        bmi = int(obj.weight) / int(obj.height) ** 2
        formatted_value = str(bmi).strip('0').strip('.').strip('0')[:3]
        formatted_value = formatted_value[:2] + '.' + formatted_value[2]
        classification = self.classify_bmi(float(formatted_value))
        if "Normal" in classification:
            return format_html(f"{formatted_value}/{classification}")
        else:
            return format_html(f"<span style='color: red;'>{formatted_value}/{classification}</span>")

    @admin.display(description='Scheduled event')
    def scheduled_event(self, mother_instance: Mother) -> str:
        # Construct the URL for the admin change page
        url = reverse('admin:mothers_questionnaire_change', args=(mother_instance.pk,))

        # Copy filters from the request and add custom parameters
        filters = {key: value for key, value in self.request.GET.items()}
        # Determine event type
        filters['add_or_change'] = 'add'

        # Construct the query string
        query_string = '&'.join([f'{key}={value}' for key, value in filters.items()])

        # Construct the final URL with query parameters
        full_url = f'{url}?{query_string}'

        user_permission = self.request.user.user_permissions
        # Return the HTML link
        if (all(perm.codename.startswith('view') for perm in user_permission.all())
                and user_permission.filter(codename='view_questionnaire').exists()):
            return format_html('add event')
        return format_html('<a href="{}">add event</a>', full_url)

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
        is_new = not bool(obj.scheduled_event.exists())
        return is_new

    @admin.display(description='Add laboratory')
    def add_laboratory_link(self, obj):
        # Generate the URL for adding an instance of the Laboratory model
        add_url = reverse('admin:mothers_laboratory_add')

        # Copy filters from the request and add custom parameters
        filters = {key: value for key, value in self.request.GET.items()}
        # Determine event type
        filters['mother'] = obj.id

        # Construct the query string
        query_string = '&'.join([f'{key}={value}' for key, value in filters.items()])

        # Construct the final URL with query parameters
        full_url = f'{add_url}?{query_string}'

        user_permission = self.request.user.user_permissions
        if (all(perm.codename.startswith('view') for perm in user_permission.all())
                and user_permission.filter(codename='view_questionnaire').exists()):
            return format_html('Add Laboratory')
        return format_html('<a href="{}">Add Laboratory</a>', full_url)
