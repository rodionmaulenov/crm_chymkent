from django.contrib import admin
from django.http import HttpRequest
from django.db import models
from django.urls import reverse
from django.utils.html import format_html

from documents.models import DocumentProxy

from mothers.admin import MotherAdmin
from mothers.models import Mother
from mothers.services.mother import on_primary_stage, get_model_objects
from mothers.services.mother_classes.url_decorators import BaseURL, QueryParameterDecorator
from mothers.services.mother_classes.permissions import PermissionCheckerFactory

Mother: models

MOTHER_ADMIN = MotherAdmin(Mother, admin.site)


@admin.register(DocumentProxy)
class DocumentProxyAdmin(admin.ModelAdmin):
    list_per_page = 10
    ordering = ('-created',)
    list_filter = ('created',)
    list_display_links = ('name',)
    fieldsets = [
        (
            None,
            {
                "fields": ['name', 'age', 'number', 'program', 'blood', 'maried', 'citizenship', 'residence',
                           'height_and_weight', 'caesarean', 'children_age', 'bad_habits'],

                'description': 'Client personal data',
            },
        )
    ]
    list_display = ('id', 'name', 'add_document', 'progress_main')

    def has_module_permission(self, request: HttpRequest) -> bool:
        base = super().has_module_permission(request)

        class_name = 'ModuleLevel'
        permission_checker = PermissionCheckerFactory.get_checker(MOTHER_ADMIN, request, class_name)
        has_perm = permission_checker.has_permission(base, on_primary_stage)
        return has_perm

    def get_queryset(self, request: HttpRequest):
        """
        A user with Basic permission has access to all instances.
        A user who is assigned custom permission to access an object receives only those objects.
        """
        self.request = request
        prefetched_list = ('state_set', 'planned_set', 'ban_set', 'stage_set', 'document_set')
        user = request.user
        mothers = Mother.objects.prefetch_related(*prefetched_list)

        if user.has_module_perms(self.opts.app_label):
            queryset = mothers
            return queryset

        queryset = get_model_objects(MOTHER_ADMIN, request).prefetch_related(*prefetched_list)
        return queryset

    def has_view_permission(self, request: HttpRequest, mother: Mother = None):
        class_name = 'ObjectListLevel'
        permission_checker = PermissionCheckerFactory.get_checker(MOTHER_ADMIN, request, class_name, 'view')
        has_perm = permission_checker.has_permission(obj=mother)
        return has_perm

    @admin.display(description='add document')
    def add_document(self, mother: Mother) -> str:
        """Add new document link."""

        filters = {key: value for key, value in self.request.GET.items()}
        filters['mother'] = mother.id
        base_url = BaseURL(reverse('admin:documents_document_add'))
        query_params = QueryParameterDecorator(base_url, filters)
        return query_params.construct_url('add new')

    def progress_main(self, obj):
        max_count = 29  # Or dynamically calculate the max count if needed
        document_count = obj.document_set.count()  # Adjust to your related documents field name
        percentage = (document_count / max_count) * 100

        # Set the fixed width of the outer div
        container_width = 60

        # Choose color based on percentage
        if percentage < 30:
            color = '#dc3545'  # Red for less than 30%
        elif percentage < 70:
            color = '#ffc107'  # Yellow for 30-69%
        else:
            color = '#28a745'  # Green for 70% and above

        add_url = reverse('admin:documents_document_add')

        # Generate the HTML for the progress bar and the styled add link
        progress_bar_html = format_html(
            '<div style="display: flex; align-items: center;">'
            '<div style="width: {}px; background-color: #eee; border: 1px solid #ccc; '
            'border-radius: 10px; position: relative; overflow: hidden;">'
            '<div style="width: {}%; background-color: {}; height: 9px; border-radius: 10px;"></div>'
            '</div>'
            '<a href="{}" class="add-link" style="padding: 3px 5px; margin-left: 5px; '
            'text-decoration: none;">'
            '<span style="color: #28a745; font-size: 20px; font-weight: bold;">+</span> Add</a>'
            '</div>',
            container_width,
            percentage,
            color,
            add_url
        )

        return progress_bar_html

    progress_main.short_description = 'Main'
