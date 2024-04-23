from datetime import date, time
from typing import Tuple, Union, Dict, Any, Optional, List, Type

from django.forms import ModelForm
from django import forms
from django.db.models import Q, Field
from django.http import HttpRequest
from django.utils import timezone
from django.db import models
from django.templatetags.static import static
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe

from mothers.models import Mother, State, Planned
from mothers.forms import StateAdminForm

Mother: models
State: models

User = get_user_model()


def filters_datetime(obj: Mother = None) -> Q:
    """Generates query filters for 'Condition' objects based on the current date and time."""

    current_date = timezone.now().date()
    current_time = timezone.now().time()

    datetime_filters = (
                               Q(state__scheduled_date=current_date, state__scheduled_time__lte=current_time) |
                               Q(state__scheduled_date__lt=current_date)
                       ) & Q(state__finished=False)

    if obj:
        datetime_filters = datetime_filters & Q(id=obj.pk)

    return datetime_filters


def filters_created(obj: Mother) -> Q:
    """Generates query filters for 'Condition' objects based on state created or not"""
    created = (
            Q(state__condition=State.ConditionChoices.CREATED) &
            Q(state__finished=True, id=obj.pk)
    )
    return created


def filtered_mothers(for_datetime: Q) -> bool:
    """Evaluates whether there are any Mother objects that match the given query filters."""
    return Mother.objects.filter(for_datetime).exists()


def render_icon(is_success: bool) -> str:
    """
    Render green icon if True else red icon
    """
    icon_color = 'green' if is_success else 'red'
    icon_path = static(f'mothers/icons/{icon_color}_check_mark.jpg')
    return mark_safe(
        f'<img src="{icon_path}" alt="{"Success" if is_success else "Failure"}" style="width: 18px; height: 20px;"/>'
    )


def get_mother_id_from_url(request: HttpRequest, key: str) -> int:
    """
    In url from GET queryset obtain id by key
    """
    mother_id = request.GET.get(key)
    return mother_id


def cleaned_date_time_and_condition(cleaned_data: Dict[str, Any]) -> Tuple[date, time, str, str]:
    """
    Extracts scheduled date, scheduled time, and condition from cleaned data.
    """
    scheduled_time = cleaned_data.get("scheduled_time")
    scheduled_date = cleaned_data.get("scheduled_date")
    condition = cleaned_data.get('condition')
    reason = cleaned_data.get('reason')
    return scheduled_date, scheduled_time, condition, reason


def validate_empty_condition(form: StateAdminForm, cleaned_data: Dict[str, Any]) -> None:
    """
    Checks reason exists if condition is empty.
    """
    _, _, condition, reason = cleaned_date_time_and_condition(cleaned_data)
    empty_condition = condition is None or condition == ''

    if empty_condition and not reason:
        form.add_error('reason', "Specify understandable reason for empty state")


def if_field_error_exists(form: StateAdminForm, cleaned_data: Dict[str, Any]) -> None:
    """
    Finally, if from only single method error exists, then break validation and error display at the top of the field.
    """
    errors = form.errors
    functions = [
        validate_empty_condition,
    ]
    for func in functions:
        func(form, cleaned_data)
        if errors: break


def initialize_form_fields(form_instance, request: Optional[HttpRequest]) -> None:
    """
    Initializes form fields 'scheduled_date' and 'scheduled_time' with local datetime values if applicable.
    """
    from mothers.services.mother import convert_utc_to_local

    scheduled_date = form_instance.instance.scheduled_date
    scheduled_time = form_instance.instance.scheduled_time

    if form_instance.instance.pk and request:
        if scheduled_date and scheduled_time:
            local_datetime = convert_utc_to_local(request, scheduled_date, scheduled_time)
            if local_datetime:
                form_instance.initial['scheduled_date'] = local_datetime.date()
                form_instance.initial['scheduled_time'] = local_datetime.time()


def hide_mother_field_on_add(form: ModelForm) -> None:
    """
    Hides the mother field if this is a new instance (i.e., not yet saved in the database).
    """
    if not form.instance.pk and 'mother' in form.fields:
        form.fields['mother'].widget = forms.HiddenInput()


def set_initial_mother_value_on_add(form: ModelForm, request: Optional[HttpRequest]) -> None:
    """
    Sets the initial value for the mother field based on the mother ID from the URL, if this is a new instance.
    """
    if not form.instance.pk and request:
        mother_id = get_mother_id_from_url(request, 'mother')
        if mother_id:
            form.initial['mother'] = mother_id


def extract_choices(db_field: Field) -> List[Tuple[Any, Any]]:
    """
    Extracts the choices from the database field.
    """
    return db_field.get_choices(include_blank=db_field.blank, blank_choice=[('', '---------')])


def is_add_action(obj: State) -> bool:
    """
    Determines whether the current action is 'add'.

    :return: True if it's an 'add' action, False otherwise.
    """
    return not (obj and obj.pk)


def filter_choices(obj: State, choices: List[Tuple[Any, Any]]) -> List[Tuple[Any, Any]]:
    """
    Filters choices based on the action type (add or change).
    """
    if is_add_action(obj):
        return [choice for choice in choices if choice[0] not in ('created',)]
    else:
        # Logic for filtering choices during 'change' action
        return [choice for choice in choices if choice[0] not in ('created',)]


def inject_request_into_form(form: Type[forms.ModelForm], request: HttpRequest) -> Type[forms.ModelForm]:
    """
    Wraps the form class to inject the request into its kwargs.
    """

    class RequestForm(form):
        def __new__(cls, *args, **local_kwargs):
            local_kwargs['request'] = request
            return form(*args, **local_kwargs)

    return RequestForm


def convert_to_utc_and_save(request: HttpRequest, obj: Union[State, Planned]) -> None:
    """
    Converts the scheduled date and time from the user's local timezone to UTC.
    """
    from mothers.services.mother import convert_local_to_utc

    if obj.scheduled_date and obj.scheduled_time:
        utc_aware_datetime = convert_local_to_utc(request, obj)
        obj.scheduled_date = utc_aware_datetime.date()
        obj.scheduled_time = utc_aware_datetime.time()


def adjust_button_visibility(context: Dict[str, Any], add: bool, change: bool) -> None:
    """
    Adjusts the visibility of form buttons in the admin change form context.
    """
    # If we are adding a new instance (not changing), adjust the visibility of buttons.
    if add or change:
        context['show_save_and_add_another'] = False  # Remove "Save and add another" button
        context['show_save_and_continue'] = False  # Remove "Save and continue editing" button
        context['show_save'] = True  # Ensure "Save" button is visible
