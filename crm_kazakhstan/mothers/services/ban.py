from django.http import HttpRequest
from django.contrib.admin import ModelAdmin
from django.contrib import admin
from django.urls import reverse
from django.db.models import QuerySet

from mothers.services.mother import get_model_objects
from mothers.admin import MotherAdmin
from mothers.models import Ban, Mother, Stage


def on_ban_stage(queryset: QuerySet) -> QuerySet:
    """
    Get only mothers where Stage is Ban
    """
    return queryset.filter(mother__stage__stage=Stage.StageChoices.BAN, mother__stage__finished=False)


def view_perm(adm: ModelAdmin, request: HttpRequest, obj: Ban, action: str) -> bool:
    """
    Object level or model level resolution allows viewing of a specific object.
    List of instances can view the user who is assigned the model permission level
    or user which has related mother instances.
    """
    app_label = adm.opts.app_label
    model_name = adm.opts.model_name
    permission = f'{app_label}.{action}_{model_name}'
    obj_perm = request.user.has_perm(permission, obj)
    perm = request.user.has_perm(permission)

    if obj:
        return obj_perm or perm

    mother_admin = MotherAdmin(Mother, admin.site)
    users_objs = get_model_objects(mother_admin, request, ).exists()
    return perm or users_objs


def add_perm(request: HttpRequest, add: ModelAdmin.has_add_permission) -> bool:
    """
    Can add only when on mothers_add url
    """
    ban_add_url = reverse('admin:mothers_ban_add')
    if ban_add_url in request.get_full_path():
        mother_admin = MotherAdmin(Mother, admin.site)
        users_objs = get_model_objects(mother_admin, request).exists()
        return users_objs or add
    return False
