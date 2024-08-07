from django.contrib import admin
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from guardian.shortcuts import get_objects_for_user

from mothers.models import Mother
from mothers.services.short_plan import get_mothers_with_recent_incomplete_events, get_mother_that_event_time_has_come

User = get_user_model()


class NewEventOccursFilter(admin.SimpleListFilter):
    title = _('the event has occurred')
    parameter_name = 'an_event_occurred'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        new_event_occurs = get_mother_that_event_time_has_come(qs)
        if new_event_occurs:
            yield 'new_event', 'new event'

    def queryset(self, request, queryset):
        if self.value() == 'new_event':
            return get_mother_that_event_time_has_come(queryset)


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
        users_objs = get_mothers_with_recent_incomplete_events(users_objs)
        return users_objs


class IsNewFilter(admin.SimpleListFilter):
    title = _('is new?')
    parameter_name = 'new_or_old'

    def lookups(self, request, model_admin):
        return [
            ('new', _('New')),
            ('old', _('Old')),
        ]

    def queryset(self, request, queryset):
        queryset = queryset.annotate(scheduled_events_count=Count('scheduled_event'))
        if self.value() == 'old':
            return queryset.filter(scheduled_events_count__gte=2)
        elif self.value() == 'new':
            return queryset.filter(scheduled_events_count=1)
        return queryset
