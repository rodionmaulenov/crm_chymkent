from django.contrib import admin
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from guardian.shortcuts import get_objects_for_user

from mothers.models import Mother
from mothers.services.application import convert_utc_to_local

User = get_user_model()


class DayOfWeekFilter(admin.SimpleListFilter):
    title = _('day of the week')
    parameter_name = 'created_day_of_week'

    def lookups(self, request, model_admin):
        return [
            ('0', _('Monday')),
            ('1', _('Tuesday')),
            ('2', _('Wednesday')),
            ('3', _('Thursday')),
            ('4', _('Friday')),
            ('5', _('Saturday')),
            ('6', _('Sunday')),
        ]

    def queryset(self, request, queryset):

        if self.value():
            day_of_week = int(self.value())

            # Convert each created datetime to the user's local timezone and filter by day of week
            matching_ids = []
            for obj in queryset:
                local_created = convert_utc_to_local(request, obj.created)
                if local_created.weekday() == day_of_week:
                    matching_ids.append(obj.id)

            return queryset.filter(id__in=matching_ids)
        return queryset


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

        users_objs = get_objects_for_user(user, perms=custom_permission_name, klass=klass).filter(
            Q(age__isnull=True) | Q(residence__isnull=True) | Q(height__isnull=True) | Q(weight__isnull=True) |
            Q(caesarean__isnull=True) | Q(children__isnull=True)
        )
        return users_objs
