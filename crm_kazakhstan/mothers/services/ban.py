from django.http import HttpRequest
from django.contrib.admin import ModelAdmin
from django.urls import reverse
from django.db.models import QuerySet
from django.utils.html import format_html

from mothers.services.mother import get_model_objects
from mothers.models import Ban, Stage


def on_ban_stage(queryset: QuerySet) -> QuerySet:
    """
    ``Mother`` instances from Stage is Ban.
    """
    return queryset.filter(mother__stage__stage=Stage.StageChoices.BAN, mother__stage__finished=False, banned=False)


def has_permission(adm: ModelAdmin, request: HttpRequest, action: str, obj: Ban = None) -> bool:
    """
    User has obj level and list level permission when has model ``view, change, delete`` and in case
    when user is assigned custom permission ``ban_state`` on some ``Ban`` instance.
    """
    custom_act = 'mothers.ban_state'
    _meta = adm.opts
    app_label = _meta.app_label
    model_name = _meta.model_name
    base_perm = f'{app_label}.{action}_{model_name}'

    obj_lvl_perm = request.user.has_perm(custom_act, obj)
    modl_lvl_perm = request.user.has_perm(base_perm)

    if obj is not None:
        return obj_lvl_perm or modl_lvl_perm

    users_objs = get_model_objects(adm, request, custom_act)
    data_exists = on_ban_stage(users_objs).exists()
    return data_exists or modl_lvl_perm


def after_add_message(obj: Ban) -> str:
    url = reverse('admin:mothers_mother_change', args=[obj.mother.id])
    added_message = format_html(
        f'<strong><a href="{url}">{obj.mother}</a></strong> add to ban successfully.'
    )
    return added_message
