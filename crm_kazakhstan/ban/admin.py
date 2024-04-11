from django.contrib import admin, messages
from django.db import models
from django.http import HttpRequest
from django.utils.html import format_html
from django.shortcuts import redirect
from django.urls import reverse

from ban.models import BanProxy

from mothers.admin import MotherAdmin
from mothers.inlines import PlannedInline, StateInline, BanInline
from mothers.models import Mother, Stage
from mothers.services.mother import get_model_objects, on_ban_stage, tuple_inlines
from mothers.services.mother_classes.permissions import PermissionCheckerFactory

Mother: models


@admin.register(BanProxy)
class BanProxyAdmin(admin.ModelAdmin):
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

        mother_admin = MotherAdmin(Mother, admin.site)
        class_name = 'ModulePermission'
        permission_checker = PermissionCheckerFactory.get_checker(mother_admin, request, class_name)
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

        mother_admin = MotherAdmin(Mother, admin.site)
        mothers = get_model_objects(mother_admin, request).prefetch_related(
            'state_set', 'planned_set', 'ban_set', 'stage_set'
        )
        queryset = on_ban_stage(mothers)
        return queryset

    def has_view_permission(self, request: HttpRequest, mother: Mother = None):
        mother_admin = MotherAdmin(Mother, admin.site)
        class_name = 'ObjectListLevelPermission'
        permission_checker = PermissionCheckerFactory.get_checker(mother_admin, request, class_name)
        has_perm = permission_checker.has_permission('view', on_ban_stage, obj=mother)
        return has_perm

    @admin.display(description='comment', empty_value='')
    def comment(self, mother: Mother) -> str:
        return mother.ban_set.latest('created').comment

    @admin.action(description='out from ban')
    def out_from_ban(self, request, queryset):
        """Move on primary stage."""
        for mother in queryset:
            stage = mother.stage_set.filter(finished=False).first()
            stage.finished = True
            stage.save()
            new_stage = Stage(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)
            new_stage.save()

            self.message_user(
                request,
                format_html(f'<b>{mother}</b> has successfully returned from ban'),
                messages.SUCCESS,
            )

        mother_changelist = reverse('admin:mothers_mother_changelist')
        return redirect(mother_changelist)
