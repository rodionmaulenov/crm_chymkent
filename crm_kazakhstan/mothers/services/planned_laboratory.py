from django.db.models import Q, QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from mothers.admin import MotherAdmin
from mothers.models import Mother
from guardian.shortcuts import get_objects_for_user
from django.contrib import admin


def mothers_which_on_laboratory_stage(Mothers_queryset: QuerySet) -> QuerySet:
    """
    Retrieves Mother instances which planned laboratory visit or wait doctor answer.
    """

    queryset = Mothers_queryset.filter(
        Q(laboratories__is_completed=False) |
        Q(laboratories__doctoranswer__is_completed=False)
    )

    return queryset


def get_filter_choices_for_laboratories(queryset):
    choices = []

    # Check if 'not_visit' condition has results
    not_visit = queryset.filter(
        Q(laboratories__is_completed=False) &
        Q(laboratories__is_came=False) &
        Q(laboratories__scheduled_time__lte=timezone.now())
    )
    if not_visit.exists():
        choices.append({'value': 'not_visit', 'display': _('Did not visit')})

    # Check if 'visit' condition has results
    already_visit = queryset.filter(
        Q(laboratories__is_completed=False) &
        Q(laboratories__is_came=True) &
        Q(laboratories__scheduled_time__lte=timezone.now())
    )
    if already_visit.exists():
        choices.append({'value': 'visit', 'display': _('Already visit')})

    # Check if 'new_visit' condition has results
    new_visit = queryset.filter(
        Q(laboratories__is_completed=False) &
        Q(laboratories__is_came__exact='') &
        Q(laboratories__scheduled_time__lte=timezone.now())
    )
    if new_visit.exists():
        choices.append({'value': 'new_visit', 'display': _('New visit')})

    return choices


def get_users_objs(user, queryset):
    """
    Get all mothers instance that belong to specific user.
    """
    mother_admin = MotherAdmin(Mother, admin.site)
    mother_model_name = mother_admin.opts.model_name
    custom_permission_name = f'{mother_model_name}_{user.username}'.lower()

    users_objs = get_objects_for_user(user, perms=custom_permission_name, klass=queryset)
    users_objs = mothers_which_on_laboratory_stage(users_objs)
    return users_objs
