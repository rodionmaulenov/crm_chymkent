from django.urls import reverse
from django.db.models import QuerySet
from django.utils.html import format_html
from django.contrib.admin import ModelAdmin
from django.http import HttpRequest

from mothers.models import Ban, Stage
from mothers.services.mother import get_model_objects


def on_ban_stage(queryset: QuerySet) -> QuerySet:
    """
    Mother instance locate on ban stage.
    """
    return queryset.filter(mother__stage__stage=Stage.StageChoices.BAN, mother__stage__finished=False, banned=False)


def has_permission(adm: ModelAdmin, request: HttpRequest, action: str, obj: Ban = None) -> bool:
    """
    The user has permission to access the object and list level or not depending on what permission they have.
    """
    user = request.user
    username = user.username
    stage = user.stage
    _meta = adm.opts
    app = _meta.app_label
    model = _meta.model_name

    base_perm = f'{app}.{action}_{model}'
    custom_perm = f'{stage}_{model}_{username}'.lower()

    custom = user.has_perm(custom_perm, obj)
    base = user.has_perm(base_perm)

    if obj is not None:
        return custom or base

    users_objs = get_model_objects(adm, request, stage)
    data_exists = on_ban_stage(users_objs).exists()

    return data_exists or base


def after_add_message(obj: Ban) -> str:
    url = reverse('admin:mothers_mother_change', args=[obj.mother.id])
    added_message = format_html(
        f'<strong><a href="{url}">{obj.mother}</a></strong> add to ban successfully.'
    )
    return added_message
