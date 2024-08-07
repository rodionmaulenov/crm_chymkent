from django.contrib import admin
from django.utils import timezone
from guardian.shortcuts import get_objects_for_user
from mothers.admin import MotherAdmin
from mothers.models.mother import PlannedLaboratory, Mother
from django.urls import reverse
from django.utils.html import format_html

from mothers.services.planned_laboratory import mothers_which_on_laboratory_stage


@admin.register(PlannedLaboratory)
class PlannedLaboratoryAdmin(admin.ModelAdmin):
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
    list_display = 'name', 'change_laboratory_link'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = None

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request):
        if not request.user.is_authenticated:
            return False

        view_laboratory = super().has_module_permission(request)

        queryset = mothers_which_on_laboratory_stage(Mother.objects.all())

        mother_admin = MotherAdmin(Mother, admin.site)
        mother_model_name = mother_admin.opts.model_name
        custom_permission_name = f'{mother_model_name}_{request.user.username}'.lower()
        klass = mother_admin.opts.model

        users_objs = get_objects_for_user(request.user, perms=custom_permission_name, klass=klass)
        users_objs = mothers_which_on_laboratory_stage(users_objs)

        return bool(users_objs) or (view_laboratory and queryset)

    def get_queryset(self, request):
        self.request = request

        queryset = mothers_which_on_laboratory_stage(Mother.objects.all())

        mother_admin = MotherAdmin(Mother, admin.site)
        mother_model_name = mother_admin.opts.model_name
        custom_permission_name = f'{mother_model_name}_{request.user.username}'.lower()
        klass = mother_admin.opts.model
        user_permission = request.user.user_permissions

        users_objs = get_objects_for_user(request.user, perms=custom_permission_name, klass=klass)
        users_objs = mothers_which_on_laboratory_stage(users_objs)

        if (all(perm.codename.startswith('view') for perm in user_permission.all())
                and user_permission.filter(codename='view_plannedlaboratory').exists()):
            return queryset

        return users_objs

    @admin.display(description='Add laboratory')
    def change_laboratory_link(self, mother_instance):
        laboratory = mother_instance.laboratories.order_by('-id').first()
        # Generate the URL for adding an instance of the Laboratory model
        add_url = reverse('admin:mothers_laboratory_change', args=(laboratory.id,))

        # Copy filters from the request and add custom parameters
        filters = {key: value for key, value in self.request.GET.items()}
        # Determine event type
        filters['mother'] = mother_instance.id

        # Construct the query string
        query_string = '&'.join([f'{key}={value}' for key, value in filters.items()])

        user_permission = self.request.user.user_permissions
        only_view_perm = (all(perm.codename.startswith('view') for perm in user_permission.all())
                          and user_permission.filter(codename='view_plannedlaboratory').exists())

        # Construct the final URL with query parameters
        full_url = f'{add_url}?{query_string}'
        if laboratory.scheduled_time <= timezone.now() or only_view_perm:
            return format_html('Change Laboratory')
        return format_html('<a href="{}">Change Laboratory</a>', full_url)
