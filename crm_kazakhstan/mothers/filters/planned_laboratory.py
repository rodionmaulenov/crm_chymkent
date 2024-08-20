from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model
from guardian.shortcuts import get_objects_for_user
from mothers.models import Mother
from mothers.services.planned_laboratory import mothers_which_on_laboratory_stage

User = get_user_model()


class TimeToVisitLaboratoryFilter(admin.SimpleListFilter):
    title = _('time to visit')
    parameter_name = 'time_new_visit'

    def lookups(self, request, model_admin):
        mothers_queryset = model_admin.get_queryset(request)
        time_new_visit = mothers_queryset.filter(Q(laboratories__is_completed=False) &
                                                 Q(laboratories__scheduled_time__lte=timezone.now()))
        if time_new_visit:
            yield 'new_visit', _('New Visit')

    def queryset(self, request, mothers_queryset):
        if self.value() == 'new_visit':
            return mothers_queryset.filter(Q(laboratories__is_completed=False) &
                                           Q(laboratories__scheduled_time__lte=timezone.now()))


class UsersObjectsFilter(admin.SimpleListFilter):
    title = _('users objects')
    parameter_name = 'username'

    def lookups(self, request, model_admin):
        users_with_country = User.objects.exclude(Q(country__isnull=True) | Q(country=''))

        lookups_list = []
        for user in users_with_country:
            if bool(self.get_users_objs(user)):
                lookups_tuple = (user.username, _(f'{user.get_country_display()} {user.username}'))
                lookups_list.append(lookups_tuple)
        return lookups_list

    def queryset(self, request, queryset):
        username = self.value()
        if username is not None:
            user = User.objects.filter(username=username).first()
            users_objs = self.get_users_objs(user)
            return users_objs

    @staticmethod
    def get_users_objs(user):
        from mothers.admin import MotherAdmin

        mother_admin = MotherAdmin(Mother, admin.site)
        mother_model_name = mother_admin.opts.model_name
        custom_permission_name = f'{mother_model_name}_{user.username}'.lower()
        klass = mother_admin.opts.model

        users_objs = get_objects_for_user(user, perms=custom_permission_name, klass=klass)
        users_objs = mothers_which_on_laboratory_stage(users_objs)
        return users_objs
