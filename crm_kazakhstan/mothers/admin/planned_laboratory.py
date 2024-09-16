from django.contrib import admin
from guardian.shortcuts import get_objects_for_user
from mothers.admin import MotherAdmin
from mothers.filters.planned_laboratory import TimeToVisitLaboratoryFilter, UsersObjectsFilter
from mothers.inlines.laboratory import LaboratoryInline
from mothers.models.mother import PlannedLaboratory, Mother, AnalysisType, Laboratory
from django.urls import reverse
from django.utils.html import format_html
from mothers.services.application import convert_utc_to_local
from mothers.services.planned_laboratory import mothers_which_on_laboratory_stage, get_users_objs, \
    get_filter_choices_for_laboratories
from django.http import JsonResponse
import json
from django.urls import path
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(PlannedLaboratory)
class PlannedLaboratoryAdmin(admin.ModelAdmin):
    list_per_page = 5
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
    list_display = 'name', 'change_laboratory_link', 'custom_scheduled_time', 'custom_analysis_type',
    inlines = [LaboratoryInline, ]
    list_filter = [TimeToVisitLaboratoryFilter, UsersObjectsFilter]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = None

    class Media:
        js = 'planned_laboratory/js/redirect_to_tab.js', \
            'planned_laboratory/js/rename_tab.js', \
            'planned_laboratory/js/save_is_completed.js', \
            'planned_laboratory/js/filters/ajax_filters.js',

        css = {
            'all': ('planned_laboratory/css/button_is_completed.css', 'planned_laboratory/css/filters_animation.css')
        }

    def get_list_display(self, request):
        if request.GET.get('time_new_visit') == 'new_visit':
            return ['name', 'custom_scheduled_time', 'custom_analysis_type']
        if request.GET.get('time_new_visit') == 'not_visit':
            return ['name', 'custom_scheduled_time', 'custom_analysis_type', 'is_completed_checkbox']
        return super().get_list_display(request)

    def get_list_filter(self, request):
        user_permission = request.user.user_permissions
        if not self.get_queryset(request).exists():
            return []
        if (all(perm.codename.startswith('view') for perm in user_permission.all())
                and user_permission.filter(codename='view_plannedlaboratory').exists()):
            return [TimeToVisitLaboratoryFilter, UsersObjectsFilter]
        return [TimeToVisitLaboratoryFilter, UsersObjectsFilter]

    def has_view_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

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
            return users_objs

        return queryset

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
        # laboratory.scheduled_time <= timezone.now()
        if only_view_perm:
            return format_html('Change Laboratory')
        return format_html('<a href="{}">Change Laboratory</a>', full_url)

    @admin.display(description='Scheduled time')
    def custom_scheduled_time(self, obj):
        laboratory = obj.laboratories.filter(is_completed=False).first()
        local_datetime = convert_utc_to_local(self.request, laboratory.scheduled_time)
        formatted_time = local_datetime.strftime("%d %B, %A %H:%M")
        return formatted_time

    @admin.display(description='Analysis type')
    def custom_analysis_type(self, obj):
        files = ''
        laboratory = obj.laboratories.filter(is_completed=False).first()
        for num, analyze_tye in enumerate(laboratory.analysis_types.all()):
            files += f'{num + 1}.{analyze_tye.get_name_display()}</a><br>'
        return format_html(files)

    @admin.display(description='Complete')
    def is_completed_checkbox(self, mother_instance):
        checkbox_html = format_html(
            '<input type="checkbox" class="is-new-checkbox" data-mother-id="{}">',
            mother_instance.pk,
        )
        return checkbox_html

    def changelist_view(self, request, extra_context=None):

        # if not queryset.exists():
        #     return redirect(reverse('admin:index'))

        extra_context = extra_context or {}
        extra_context['show_update_button'] = request.GET.get('time_new_visit') == 'not_visit'
        extra_context['update_url'] = reverse('admin:update_is_completed')

        return super().changelist_view(request, extra_context=extra_context)

    @staticmethod
    def update_is_completed(request):
        # this method update mother related laboratory instance 'is_completed' field
        if request.method == 'POST':
            data = json.loads(request.body)
            mother_ids = data.get('mother_ids', [])
            for mother_id in mother_ids:
                mother_instance = Mother.objects.get(pk=mother_id)
                laboratory = Laboratory.objects.filter(mother=mother_instance, is_came=False,
                                                       is_completed=False).first()
                if laboratory:
                    laboratory.is_completed = not laboratory.is_completed
                    laboratory.save()
            return JsonResponse({'status': 'success'})

    def get_filter_choices(self, request):
        mothers_queryset = self.get_queryset(request)
        choices = get_filter_choices_for_laboratories(mothers_queryset)
        return JsonResponse({'choices': choices})


    def get_users_objects_choices(self, request):
        queryset = self.get_queryset(request)
        users_with_country = User.objects.exclude(Q(country__isnull=True) | Q(country=''))

        choices = []
        for user in users_with_country:
            if bool(get_users_objs(user, queryset)):
                display_text = f'{user.get_country_display()} {user.username}'
                choices.append({'value': user.username, 'display': display_text})

        return JsonResponse({'choices': choices})

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('update_is_completed/', self.admin_site.admin_view(self.update_is_completed),
                 name='update_is_completed'),
            path('get_filter_choices/', self.admin_site.admin_view(self.get_filter_choices),
                 name='get_filter_choices'),
            path('get_users_objects_choices/', self.admin_site.admin_view(self.get_users_objects_choices),
                 name='get_users_objects_choices'),
        ]
        return custom_urls + urls


@admin.register(AnalysisType)
class AnalysisTypeAdmin(admin.ModelAdmin):
    pass
