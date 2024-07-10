from django.db import models
from django.contrib.auth import get_user_model
from django.apps import apps
from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from guardian.shortcuts import assign_perm

User = get_user_model()


def assign_user(request, which_admin: admin, obj: models):
    """
    User is being assigned obj permission.
    """
    app_label = which_admin.model._meta.app_label

    user = request.user
    username = user.username
    model = obj.__class__.__name__
    codename = f'{model}_{username}'.lower()
    name = f'{model} {username}'.lower()

    model_class = apps.get_model(app_label, model)
    content_type = ContentType.objects.get_for_model(model_class)
    permission, _ = Permission.objects.get_or_create(
        codename=codename,
        name=name,
        content_type=content_type,
    )
    assign_perm(permission, user, obj)
