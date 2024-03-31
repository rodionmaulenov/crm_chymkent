import pytz

from datetime import datetime, time, date
from typing import Optional, Union
from guardian.shortcuts import get_objects_for_user
from abc import ABC, abstractmethod

from django.contrib.admin import ModelAdmin
from django.db.models import Count
from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone, formats
from django.db import models
from django.db.models import QuerySet, Q
from django.utils.html import format_html, mark_safe

from gmail_messages.models import CustomUser

from mothers.models import Stage, State, Mother, Ban

Stage: models
State: models


def convert_local_to_utc(request: HttpRequest, instance: State) -> datetime:
    """
    Converts the scheduled date and time of a Condition instance from the user's local timezone to UTC.
    """

    # Convert string to a timezone object
    user_timezone = pytz.timezone(str(request.user.timezone))

    # Combine date and time into a datetime object
    future_local_datetime = datetime.combine(instance.scheduled_date, instance.scheduled_time)

    # Make the datetime object timezone-aware in the user's local timezone
    future_local_aware = user_timezone.localize(future_local_datetime)

    # Convert the local timezone-aware datetime to UTC
    utc_datetime = future_local_aware.astimezone(pytz.utc)

    return utc_datetime


def convert_utc_to_local(request: HttpRequest, utc_date: date, utc_time: time) -> datetime:
    user_timezone = getattr(request.user, 'timezone', 'UTC')
    # Convert string to a timezone object
    user_timezone = pytz.timezone(str(user_timezone))

    # Combine UTC date and time strings into a datetime object
    utc_datetime_naive = datetime.combine(utc_date, utc_time)

    # Make the datetime object timezone-aware in UTC
    utc_datetime_aware = pytz.utc.localize(utc_datetime_naive)

    # Convert the UTC timezone-aware datetime to user's local timezone
    local_datetime = utc_datetime_aware.astimezone(user_timezone)

    return local_datetime


def on_primary_stage(queryset: QuerySet) -> QuerySet:
    """
    Gets ``Mother`` instances from ``Stage.StageChoices.PRIMARY``.
    """
    return queryset.filter(stage__stage=Stage.StageChoices.PRIMARY, stage__finished=False)


def we_are_working(queryset: QuerySet) -> QuerySet:
    """
    When `State`` becomes 'we are working'.
    """
    return queryset.filter(state__condition=State.ConditionChoices.WORKING, state__finished=False)


def convert_to_local_time(obj: Union[Mother, Ban], user_timezone: str) -> timezone.datetime:
    """
    Converts the 'date_create' of a Mother instance from UTC to the user's local timezone.
    """
    user_tz = pytz.timezone(str(user_timezone))
    return timezone.localtime(obj.created, timezone=user_tz)


def tuple_inlines(obj: Mother, inlines) -> tuple:
    """
    Get inlines if their queryset not none.
    """
    from mothers.inlines import StateInline, BanInline
    filtered_inlines = []
    for inline in inlines:
        if inline is StateInline:
            states = obj.state_set.all()
            not_one = len(states) > 1
            if not_one:
                filtered_inlines.append(inline)
        if inline is BanInline:
            bans = obj.ban_set.exists()
            if bans:
                filtered_inlines.append(inline)

    return tuple(filtered_inlines)


def output_time_format(local_scheduled_datetime: Optional[datetime]) -> str:
    """
    Formats the provided datetime. Formats as 'Day Month Hour:Minute'.
    """
    return formats.date_format(local_scheduled_datetime, "N j, Y, H:i")


def bold_datetime_format(dt: datetime) -> str:
    """
    Formats the provided datetime as 'Day Month Year / Hour:Minute' in bold.
    """
    formatted_datetime = dt.strftime("%d %B %y/%H:%M")
    return format_html(f'<strong>{formatted_datetime}</strong>')


def get_model_objects(adm: ModelAdmin, request: HttpRequest, stage: Union[Stage, CustomUser]) -> QuerySet:
    """
    Retrieves a QuerySet of objects from the model associated with the provided ModelAdmin instance (`adm`).
    The objects are filtered based on the user's permissions. It checks if the user has custom permissions
    for the objects of the model.
    Super-user gets all queryset.
    """
    user = request.user
    username = user.username
    model = adm.opts.model_name
    klass = adm.opts.model
    perms = [f'{stage}_{model}_{username}'.lower()]

    # Retrieve and return the objects for which the user has the specified permissions
    return get_objects_for_user(user=user, perms=perms, klass=klass)


def has_permission(adm: ModelAdmin, request: HttpRequest, action: str, obj: Mother = None) -> bool:
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
    data_exists = on_primary_stage(users_objs).exists()

    return data_exists or base


def get_already_created(queryset: QuerySet) -> QuerySet:
    """
    When condition instance only one, that`s mean created status
    """
    queryset = queryset.annotate(created_count=Count('state'))

    return queryset.filter(created_count=1, state__condition=State.ConditionChoices.CREATED)


def ban_query(queryset: QuerySet) -> QuerySet:
    """
    All instance which not move to ban.
    """
    return queryset.filter(ban__banned=False)


def without_plan(queryset: QuerySet) -> QuerySet:
    """
    When plan on already created mother instance not appears.
    """
    queryset = queryset.annotate(amount=Count('state'))

    return queryset.filter(amount__gte=2).exclude(state__finished=False)


def get_empty_state(queryset: QuerySet) -> QuerySet:
    """
    Objs with empty condition
    """
    return queryset.filter((Q(state__condition=State.ConditionChoices.EMPTY) | Q(state__condition=None))
                           & Q(state__finished=False))


def after_change_message(obj: Mother) -> str:
    url = reverse('admin:mothers_mother_change', args=[obj.pk])

    changed_message = format_html(
        f'Changes for <strong><a href="{url}">{obj}</a></strong> saved successfully.'
    )
    return changed_message


def link_html(url: str, text: str) -> format_html:
    """Custom link."""
    return f'<a href="{url}">{text}</a>'


def extract_from_url(request: HttpRequest, key: str, value: str) -> bool:
    """
    Checks the request URL for specific parameter.
    """
    if key in request.GET:
        from_url = request.GET[key]
        return from_url == value
    return False


def add_new(path: str, obj: Mother) -> format_html:
    """
    Add new obj related with ``Mother`` instance.
    """
    url = reverse(path)
    return format_html(f'<a href="{url}?mother={obj.pk}"><b>adding</b></a>')


def change(url: str, instance: models, text: str) -> format_html:
    """
    Custom change link.
    """
    change_url = reverse(url, args=[instance.pk])
    link = link_html(change_url, text)

    return mark_safe(link)


class Specification:
    """
    Base class for inheritance future child spec
    """

    def __init__(self, spec):
        self.spec = spec

    def is_verified(self, item):
        pass


class Filter:
    """
    Base class for inheritance future child filter
    """

    def filter(self, item, spec):
        pass


class FromUrlSpec(Specification):
    def is_verified(self, item):
        """
        Get the specific query from request session
        """
        spec = item.get(self.spec, False)
        return spec


class BaseFilter(Filter):
    def filter(self, item, spec) -> bool:
        return spec.is_verified(item)

# Command Interface
