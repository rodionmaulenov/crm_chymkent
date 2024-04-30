from django.contrib import admin
from django.db import models
from django.http import HttpRequest

from ban.inlines import BanInline
from ban.models import BanProxy

from mothers.admin import MotherAdmin
from mothers.inlines import PlannedInline, StateInline
from mothers.models import Mother
from mothers.services.mother import get_model_objects, on_ban_stage, tuple_inlines
from mothers.services.mother_classes.command_interface import FromBanCommand
from mothers.services.mother_classes.permissions import PermissionCheckerFactory

Mother: models


@admin.register(BanProxy)
class BanProxyAdmin(admin.ModelAdmin):
    _mother_admin = MotherAdmin(Mother, admin.site)
    list_per_page = 10
    search_help_text = 'Search description'
    ordering = ('-created',)
    inlines = (PlannedInline, StateInline, BanInline)
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
    list_display = ('id', 'name', 'comment')
    actions = ["out_from_ban"]

    def get_inlines(self, request, obj):
        """
        Only non-empty inline models are displayed.
        """
        inlines = super().get_inlines(request, obj)
        return tuple_inlines(obj, inlines)

    def has_module_permission(self, request: HttpRequest) -> bool:
        base = super().has_module_permission(request)

        class_name = 'ModuleLevel'
        permission_checker = PermissionCheckerFactory.get_checker(self._mother_admin, request, class_name)
        has_perm = permission_checker.has_permission(base, on_ban_stage)
        return has_perm

    def get_queryset(self, request: HttpRequest):
        """
        Get a instance of Mothers during the ban phase.

        A user with Basic permission has access to all instances.
        A user who is assigned custom permission to access an object receives only those objects.
        """
        user = request.user
        mothers = Mother.objects.prefetch_related(
            'state_set', 'planned_set', 'ban_set', 'stage_set'
        )

        if user.has_module_perms(self.opts.app_label):
            queryset = on_ban_stage(mothers)
            return queryset

        mothers = get_model_objects(self._mother_admin, request).prefetch_related(
            'state_set', 'planned_set', 'ban_set', 'stage_set'
        )
        queryset = on_ban_stage(mothers)
        return queryset

    def has_view_permission(self, request: HttpRequest, mother: Mother = None):
        class_name = 'ObjectListLevel'
        permission_checker = PermissionCheckerFactory.get_checker(self._mother_admin, request, class_name, 'view')
        has_perm = permission_checker.has_permission(on_ban_stage, obj=mother)
        return has_perm

    @admin.display(description='comment', empty_value='')
    def comment(self, mother: Mother) -> str:
        return mother.ban_set.latest('created').comment

    @admin.action(description='out from ban')
    def out_from_ban(self, request, queryset):
        """Move on primary stage."""
        leave_the_ban = FromBanCommand(self, request, queryset)
        return leave_the_ban.execute()
