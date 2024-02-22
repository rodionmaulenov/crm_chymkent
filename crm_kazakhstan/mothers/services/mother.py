import pytz

from datetime import datetime, time, date
from typing import Optional

from django.contrib.admin import ModelAdmin
from django.db.models import Count
from django.http import HttpRequest
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.utils import timezone, formats
from django.utils.http import urlencode
from django.db import models
from django.db.models import QuerySet, Q
from django.utils.html import format_html, mark_safe
from guardian.shortcuts import get_objects_for_user

from mothers.models import Stage, Condition, Mother
from mothers.services.condition import filters_datetime, filtered_mothers

Stage: models
Condition: models


def convert_local_to_utc(request: HttpRequest, instance: Condition) -> datetime:
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


def date_time_or_exception() -> None:
    """
    Check if the user has permission to access the 'planned_time' lookup.
    """
    query_datetime = filters_datetime()
    on_filtered_queryset = filtered_mothers(query_datetime)
    if not on_filtered_queryset:
        raise PermissionDenied


def on_primary_stage(queryset: QuerySet) -> QuerySet:
    """
    Get only mothers where Stage is Primary
    """
    return queryset.filter(stage__stage=Stage.StageChoices.PRIMARY, stage__finished=False)


def convert_to_local_time(obj: Mother, user_timezone: str) -> timezone.datetime:
    """
    Converts the 'date_create' of a Mother instance from UTC to the user's local timezone.
    """
    user_tz = pytz.timezone(str(user_timezone))
    return timezone.localtime(obj.date_create, timezone=user_tz)


def output_time_format(local_scheduled_datetime: Optional[datetime]) -> str:
    """
    Formats the provided datetime. Formats as 'Day Month Hour:Minute'.
    """
    return formats.date_format(local_scheduled_datetime, "j M H:i")


# def change_on_filtered_changelist(condition: Condition, condition_display: str, request: HttpRequest) -> format_html:
#     """
#     Can Change 'Condition instance' on filtered change list page.
#     """
#     local_datetime = convert_utc_to_local(request, condition.scheduled_date, condition.scheduled_time)
#     formatted_datetime = output_time_format(local_datetime)
#
#     change_url = reverse('admin:mothers_condition_change', args=[condition.pk])
#
#     css_style = get_css_style("violet-link", "rgba(138, 43, 226, 0.8)", "violet")
#     # Create link only for condition_display
#     link_html = create_link_html(change_url, "violet-link", condition_display)
#
#     # Combine the link with the formatted date, keeping the date outside of the hyperlink
#     combined_html = f'{css_style}{link_html}/<br>{formatted_datetime}'
#
#     # designate full url path for this change
#     set_url_when_change_or_add_condition_object(request)
#
#     return mark_safe(combined_html)


def get_model_objects(adm: ModelAdmin, request: HttpRequest) -> QuerySet:
    """
    Retrieves a QuerySet of objects from the model associated with the provided MotherAdmin instance (`adm`).
    The objects are filtered based on the user's permissions. It checks if the user has either 'view' or 'change'
    permissions for the objects of the model.
    """
    _meta = adm.opts
    actions = ['view', 'change']  # Define the permissions to check
    perms = [f'{perm}_{_meta.model_name}' for perm in actions]  # Construct permission codenames
    klass = _meta.model  # The model class associated with the ModelAdmin

    # Retrieve and return the objects for which the user has the specified permissions
    return get_objects_for_user(user=request.user, perms=perms, klass=klass, any_perm=True)


def has_permission(adm: ModelAdmin, request: HttpRequest, obj: Mother, action: str) -> bool:
    """
    Two type users. First see only assigned him objects. Second see all objects if he had corresponding permission.
    """
    app_label = adm.opts.app_label
    model_name = adm.opts.model_name
    permission = f'{app_label}.{action}_{model_name}'
    obj_perm = request.user.has_perm(permission, obj)
    perm = request.user.has_perm(permission)

    if obj:
        return obj_perm or perm

    user_obj = get_model_objects(adm, request)
    data_exists = on_primary_stage(user_obj).exists()
    return data_exists or perm


def get_already_created(queryset: QuerySet) -> QuerySet:
    """
    When condition instance only one, that`s mean created status
    """
    queryset = queryset.annotate(created_count=Count('condition'))

    return queryset.filter(created_count=1, condition__condition=Condition.ConditionChoices.CREATED)


def get_empty_state(queryset: QuerySet) -> QuerySet:
    """
    Objs with empty condition
    """
    return queryset.filter((Q(condition__condition=Condition.ConditionChoices.__empty__) | Q(condition__condition=None))
                           & Q(condition__finished=False))


class HTMLElement:
    """Create complex html element from simple elements"""
    indent_size = 2

    def __init__(self, name: str = '', link_class: str = '', default_color: str = '', hover_color: str = '') -> None:
        self.name = name
        self.link_class = link_class
        self.default_color = default_color
        self.hover_color = hover_color
        self.elements = []

    def __str(self, indent: int) -> str:
        """Iterates all nested attributes recursively"""
        lines = []

        if self.name:
            i = ' ' * (indent * self.indent_size)
            lines.append(f'{i}<{self.name}>')

        if self.default_color:
            i1 = ' ' * ((indent + 1) * self.indent_size)
            lines.append(f'{i1}a.{self.link_class} {{ color: {self.default_color}; }}')

        if self.hover_color:
            i1 = ' ' * ((indent + 1) * self.indent_size)
            lines.append(f'{i1}a.{self.link_class}:hover {{ color: {self.hover_color}; }}')

        for elem in self.elements:
            lines.append(elem.__str(indent + 1))

        if self.name:
            lines.append(f'{i}</{self.name}>')

        return '\n'.join(lines)

    def __str__(self):
        """Pass into __str zero indent"""
        return self.__str(0)


class HTMLBuilder:
    """Accept the html elements and construct the complex html object"""

    def __init__(self, root_name: str) -> None:
        self.root_name = root_name
        self.__root = HTMLElement(name=root_name)

    def add_child(self, link_class: str, default_color: str, hover_color: str) -> None:
        self.__root.elements.append(HTMLElement(
            link_class=link_class, default_color=default_color, hover_color=hover_color
        ))

    def __str__(self):
        return str(self.__root)


def bold_text(last_condition: Condition) -> format_html:
    """
    Retrieves the last condition for a `Mother` object, and returns its display string in a bold HTML format.
    The display string is truncated to 50 characters if it's.
    """
    obj = last_condition
    reason = obj.reason
    state = obj.condition == '__empty__'

    if not state:
        for_display = obj.get_condition_display()
    else:
        for_display = reason

    for_display = (for_display[:50] + '...') if len(for_display) > 50 else for_display
    return mark_safe(f'<strong>{for_display}</strong>')


def link_html(url: str, style: HTMLBuilder, link_class: str, text: str) -> format_html:
    """Creates reference with custom style and text."""
    return str(style) + '\n' + f'<a href="{url}" class="{link_class}">{text}</a>'


def extract_from_url(request: HttpRequest, key: str, value: str) -> bool:
    """
    Checks the request URL for specific parameter.
    """
    if key in request.GET:
        from_url = request.GET[key]
        return from_url == value


def simple_text(text: str) -> format_html:
    """When one of the related with MotherAdmin instances exist. Returns simple bold text"""
    return format_html('{}', text)


def add_new(obj: Mother, text: str, request: HttpRequest) -> format_html:
    """When noone of the related with MotherAdmin instances don`t exist and finished condition exists.
    Generates an HTML link to add a new "Condition" in the Django admin interface for a specific Mother object.
    """
    add_url = reverse('admin:mothers_condition_add')
    current_path = request.get_full_path()
    return_path = urlencode({'_changelist_filters': current_path})

    return format_html(f'<a href="{add_url}?mother={obj.pk}&{return_path}">{text}</a>')


def can_change_on_changelist(condition: Condition, text: str) -> format_html:
    """When action happens on changelist page and planned date is not occurs.
     Returns the green change reference for a specific condition instance."""

    change_url = reverse('admin:mothers_condition_change', args=[condition.pk])

    style = HTMLBuilder('style')
    style.add_child("light-green", "green", "rgba(0, 150, 0, 0.8)")

    link = link_html(change_url, style, "light-green", text)

    return mark_safe(link)


def can_not_change_on_changelist(text) -> format_html:
    """When action happens on changelist page and planned date is already occurs. Returns simple bold text."""
    return mark_safe(text)


def change_on_filtered_changelist(condition: Condition, text) -> format_html:
    """When action happens on filtered changelist page and planned date is already occurs."""

    change_url = reverse('admin:mothers_condition_change', args=[condition.pk])

    style = HTMLBuilder('style')
    style.add_child("violet-link", "rgba(138, 43, 226, 0.8)", "violet")

    link = link_html(change_url, style, "violet-link", text)

    return mark_safe(link)


class Specification:
    """Base class for inheritance future child spec"""

    def __init__(self, spec):
        self.spec = spec

    def is_verified(self, item):
        pass


class Filter:
    """Base class for inheritance future child filter"""

    def filter(self, item, spec):
        pass


class FromUrlSpec(Specification):
    def is_verified(self, item):
        """Get the specific query from request session"""
        spec = item.get(self.spec, False)
        return spec


class BaseFilter(Filter):
    def filter(self, item, spec) -> bool:
        return spec.is_verified(item)
