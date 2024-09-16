from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model
from mothers.services.planned_laboratory import get_filter_choices_for_laboratories, get_users_objs

User = get_user_model()


class TimeToVisitLaboratoryFilter(admin.SimpleListFilter):
    title = _('time to visit')
    parameter_name = 'time_new_visit'

    def lookups(self, request, model_admin):
        mothers_queryset = model_admin.get_queryset(request)
        choices = get_filter_choices_for_laboratories(mothers_queryset)
        return [(choice['value'], choice['display']) for choice in choices]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            filter_method = {
                'new_visit': Q(laboratories__is_completed=False) &
                             Q(laboratories__is_came__exact='') &
                             Q(laboratories__scheduled_time__lte=timezone.now()),

                'not_visit': Q(laboratories__is_completed=False) &
                             Q(laboratories__is_came=False) &
                             Q(laboratories__scheduled_time__lte=timezone.now()),

                'visit': Q(laboratories__is_completed=False) &
                         Q(laboratories__is_came=True) &
                         Q(laboratories__scheduled_time__lte=timezone.now())
            }

            return queryset.filter(filter_method.get(value, Q()))

        return queryset

    def choices(self, changelist):
        """
        Override the default choices method to remove the 'All' option.
        """
        # Call the super() method and exclude the 'All' option
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == str(lookup),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}),
                'display': title,
            }


class UsersObjectsFilter(admin.SimpleListFilter):
    title = _('users objects')
    parameter_name = 'username'

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)
        users_with_country = User.objects.exclude(Q(country__isnull=True) | Q(country=''))

        lookups_list = []
        for user in users_with_country:
            if bool(get_users_objs(user, queryset)):
                lookups_tuple = (user.username, _(f'{user.get_country_display()} {user.username}'))
                lookups_list.append(lookups_tuple)
        return lookups_list

    def queryset(self, request, queryset):
        username = self.value()
        if username is not None:
            user = User.objects.filter(username=username).first()
            users_objs = get_users_objs(user, queryset)
            return users_objs

    def choices(self, changelist):
        """
        Override the default choices method to remove the 'All' option.
        """
        # Call the super() method and exclude the 'All' option
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == str(lookup),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}),
                'display': title,
            }
