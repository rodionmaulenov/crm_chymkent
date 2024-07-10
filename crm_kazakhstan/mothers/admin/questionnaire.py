from typing import Dict, Any, Optional
from mothers.admin import MotherAdmin
from mothers.models.mother import Questionnaire, Mother
from django.contrib import admin
from guardian.shortcuts import get_objects_for_user
from django.db.models import Q
from django.contrib.admin.helpers import AdminForm
from mothers.services.state import adjust_button_visibility
from mothers.filters.applications import convert_utc_to_local
from django.utils.html import format_html


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_per_page = 10
    search_help_text = 'Search description'
    ordering = ('-created',)
    search_fields = 'name__icontains',
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
    list_display = 'name', 'mass_index', 'date_create'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = None

    def has_module_permission(self, request) -> bool:
        """
            Determines if the user has permission to access the module.

            1. Checks if the user is authenticated. If not, returns False.
            2. Filters the queryset to include instances where certain fields (age, residence, height,
               weight, caesarean, children) are not null.
            3. Returns True if the user has the custom permissions for any objects or the 'view_questionnaire'
               permission along with non-null field queryset.
        """
        if not request.user.is_authenticated:
            return False

        view_questionnaire = super().has_module_permission(request)

        filter_not_null_fields = (
                Q(age__isnull=False) & Q(residence__isnull=False) & Q(height__isnull=False) | Q(weight__isnull=False) &
                Q(caesarean__isnull=False) & Q(children__isnull=False)

        )

        queryset = Mother.objects.all().filter(filter_not_null_fields)

        mother_admin = MotherAdmin(Mother, admin.site)
        mother_model_name = mother_admin.opts.model_name
        custom_permission_name = f'{mother_model_name}_{request.user.username}'.lower()
        klass = mother_admin.opts.model

        users_objs = get_objects_for_user(request.user, perms=custom_permission_name, klass=klass).filter(
            filter_not_null_fields)

        return bool(users_objs) or (view_questionnaire and queryset)

    def get_queryset(self, request):
        """
            Customizes the queryset for the Mother model based on specific conditions:

            1. Filters the queryset to include instances where certain fields (age, residence, height,
               weight, caesarean, children) are not null.
            2. Checks if the user has a custom permission and filters the queryset further based on this permission.
            3. If the user has all permissions starting with 'view' and specifically the 'view_questionnaire' permission,
               returns the initially filtered queryset.
            4. Otherwise, returns the queryset filtered by both the custom permission and non-null fields.
        """
        self.request = request

        filter_not_null_fields = (
                Q(age__isnull=False) & Q(residence__isnull=False) & Q(height__isnull=False) | Q(weight__isnull=False) &
                Q(caesarean__isnull=False) & Q(children__isnull=False)

        )

        queryset = Mother.objects.all().filter(filter_not_null_fields)

        mother_admin = MotherAdmin(Mother, admin.site)
        mother_model_name = mother_admin.opts.model_name
        custom_permission_name = f'{mother_model_name}_{request.user.username}'.lower()
        klass = mother_admin.opts.model
        user_permission = request.user.user_permissions

        users_objs = get_objects_for_user(request.user, perms=custom_permission_name, klass=klass).filter(
            filter_not_null_fields)

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

        adjust_button_visibility(context, add, change)

        return super().render_change_form(request, context, add=add, change=change,
                                          form_url=form_url, obj=obj)

    @admin.display(description='Date create')
    def date_create(self, obj):
        local_datetime = convert_utc_to_local(self.request, obj.created)
        return format_html("<strong>{}</strong>", local_datetime.strftime("%A %H:%M, %d %B"))

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
