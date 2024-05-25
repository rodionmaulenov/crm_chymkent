import pytz

from datetime import datetime, time, date
from typing import Union, Optional
from urllib.parse import urlparse, urlencode
from guardian.shortcuts import get_objects_for_user

from django.contrib.admin import ModelAdmin
from django.db.models import Count
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.db import models
from django.db.models import QuerySet, Q
from django.utils.html import format_html

from mothers.models import Stage, State, Mother
from mothers.services.mother_classes.create_messages import MessageCreator
from mothers.services.mother_classes.url_decorators import BaseURL, QueryParameterDecorator, MessageDecorator

from ban.models import Ban

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


def on_first_visit_stage(queryset: QuerySet) -> QuerySet:
    """
    Gets ``Mother`` instances from ``Stage.StageChoices.PRIMARY``.
    """
    return queryset.filter(stage__stage=Stage.StageChoices.FIRST_VISIT, stage__finished=False)


def on_ban_stage(queryset: QuerySet) -> QuerySet:
    """
    Gets ``Mother`` instances from ``Stage.StageChoices.PRIMARY``.
    """
    return queryset.filter(stage__stage=Stage.StageChoices.BAN, stage__finished=False)


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

    from mothers.inlines import StateInline, PlannedInline
    from ban.inlines import BanInline
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
        if inline is PlannedInline:
            plan = obj.planned_set.exists()
            if plan:
                filtered_inlines.append(inline)
    return tuple(filtered_inlines)


def bold_datetime_format(dt: datetime) -> str:
    """
    Formats the provided datetime as 'Day Month Year / Hour:Minute' in bold.
    """
    formatted_datetime = dt.strftime("%d %B %y/%H:%M")
    return format_html(f'<strong>{formatted_datetime}</strong>')


def get_model_objects(adm: ModelAdmin, request: HttpRequest) -> QuerySet:
    """
    Retrieves a QuerySet of objects from the model associated with the provided ModelAdmin instance (`adm`).
    The objects are filtered based on the user's permissions. It checks if the user has custom permissions
    for the objects of the model.
    Super-user gets all queryset.
    """
    user = request.user
    stage = user.stage
    username = user.username
    model = adm.opts.model_name
    klass = adm.opts.model
    perms = [f'{stage}_{model}_{username}'.lower()]

    # Retrieve and return the objects for which the user has the specified permissions
    return get_objects_for_user(user=user, perms=perms, klass=klass)


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
    return queryset.filter((Q(state__condition='') | Q(state__condition=None))
                           & Q(state__finished=False))


def extract_from_url(request: HttpRequest, key: str, value: str) -> bool:
    """
    Checks the request URL for specific parameter.
    """
    if key in request.GET:
        from_url = request.GET[key]
        return from_url == value
    return False


def set_url(request: HttpRequest, path: str, text: str = None) -> str:
    filters = {key: value for key, value in request.GET.items()}

    parsed_url = urlparse(path)
    path_only = parsed_url.path
    query_string = parsed_url.query

    if query_string:
        filters['mother'] = query_string.split('=')[1]

    base_url = BaseURL(path_only)
    query_params = QueryParameterDecorator(base_url, filters)
    uri = query_params.construct_url(text)
    return uri


def redirect_to(request: HttpRequest, obj: models.Model, text: str, url_collection: dict,
                level: int) -> HttpResponseRedirect:
    message_creator = MessageCreator(obj, url_collection['message_url'])
    message = message_creator.message(text)

    filters = {key: value for key, value in request.GET.items()}
    if filters.get('mother', []): del filters['mother']

    base_url = BaseURL(url_collection['base_url'])
    query_params = QueryParameterDecorator(base_url, filters)
    message_url = MessageDecorator(query_params, request, message, level)
    return HttpResponseRedirect(message_url.construct_url())


def simple_redirect(request: HttpRequest, url: str, message: str, level: int):
    base_url = BaseURL(url)
    message_url = MessageDecorator(base_url, request, message, level)
    return HttpResponseRedirect(message_url.construct_url())


def check_cond(request: HttpRequest, mother: Mother, model: str) -> Optional[set_url]:
    if model == 'state':
        iterable = mother.state.exists(), mother.plan.exists()
        mothers_obj = mother.state.first()
    else:
        iterable = mother.plan.exists(), mother.state.exists()
        mothers_obj = mother.plan.first()

    match iterable:
        case (True, _):
            url = reverse(f'admin:mothers_{model}_change', args=[mothers_obj.id])
            return set_url(request, url, mothers_obj)
        case (False, False):
            url = reverse(f'admin:mothers_{model}_add') + '?' + urlencode({'mother': mother.pk})
            return set_url(request, url, 'add new')
        case (False, True):
            return
