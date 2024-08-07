from typing import Any, Dict, Optional
from django.contrib.admin.helpers import AdminForm
from django.db import models
from django.db.models import Q
from django.utils.html import format_html
from django.contrib import admin
from django.forms import ModelForm
from django.utils import timezone
from guardian.shortcuts import get_objects_for_user
from mothers.filters.applications import DayOfWeekFilter, convert_utc_to_local, UsersObjectsFilter
from mothers.models import Mother
from mothers.services.application import assign_user

# Globally disable delete selected
admin.site.disable_action('delete_selected')

ContentType: models


@admin.register(Mother)
class MotherAdmin(admin.ModelAdmin):
    list_per_page = 10
    search_help_text = 'Search description'
    ordering = ('-created',)
    list_filter = (DayOfWeekFilter, UsersObjectsFilter)
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
    list_display = 'name', 'age', 'residence', 'height', 'weight', 'caesarean', 'blood', 'maried', 'date_create'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = None
        
    def get_list_filter(self, request):
        user_permission = request.user.user_permissions
        if not self.get_queryset(request).exists():
            return []
        if (all(perm.codename.startswith('view') for perm in user_permission.all())
                and user_permission.filter(codename='view_mother').exists()):
            return [DayOfWeekFilter, UsersObjectsFilter]
        return [DayOfWeekFilter]

    @admin.display(description='Date create')
    def date_create(self, obj):
        local_datetime = convert_utc_to_local(self.request, obj.created)
        return format_html("<strong>{}</strong>", local_datetime.strftime("%A %H:%M"))

    def get_queryset(self, request):
        """
           Returns a queryset of Mother instances, filtered for null fields and user-specific permissions.

           This method:
           1. Retrieves the initial queryset.
           2. Filters instances where any of the fields (age, residence, height, weight, caesarean, children) are null.
           3. Constructs a custom permission name based on the model name and user's username.
           4. Retrieves objects the user has permissions for and applies the same filter.
           5. Returns the user-specific filtered queryset if it exists, otherwise returns the general filtered queryset.
        """

        self.request = request
        
        filter_null_fields = (
                Q(age__isnull=True) | Q(residence__isnull=True) | Q(height__isnull=True) | Q(weight__isnull=True) |
                Q(caesarean__isnull=True) | Q(children__isnull=True)
        )
        queryset = super().get_queryset(request).filter(filter_null_fields)

        mother_model_name = self.opts.model_name
        custom_permission_name = f'{mother_model_name}_{request.user.username}'.lower()
        klass = self.opts.model
        user_permission = request.user.user_permissions

        users_objs = get_objects_for_user(request.user, perms=custom_permission_name, klass=klass).filter(
            filter_null_fields)

        if (all(perm.codename.startswith('view') for perm in user_permission.all())
                and user_permission.filter(codename='view_mother').exists()):
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

    def save_model(self, request, obj: Mother, form: ModelForm, change: bool) -> None:
        """
        Handles the saving of a Application instance in the Django admin interface.
        Converts scheduled time to UTC, saves the instance, and assigns permissions if it's a new instance.
        """
        obj.created = timezone.now()

        is_new = not obj.pk  # Check if the object is new (has no primary key yet)

        super().save_model(request, obj, form, change)

        if is_new:
            mother_admin = self
            assign_user(request, mother_admin, obj)
