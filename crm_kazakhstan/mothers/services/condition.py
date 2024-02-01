from datetime import date, time
from typing import Tuple, Union, Dict, Any, Optional, List, Type

from django.contrib.admin import ModelAdmin
from django.urls import reverse
from django.utils.html import format_html
from guardian.shortcuts import assign_perm

from django import forms
from django.contrib import messages
from django.db.models import Q, Field
from django.http import HttpRequest, HttpResponseRedirect
from django.utils import timezone
from django.db import models
from django.utils import formats
from django.templatetags.static import static
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe

from mothers.models import Mother, Condition
from mothers.forms import ConditionAdminForm

Mother: models
Condition: models

User = get_user_model()


def filter_condition_by_date_time() -> Q:
    """
    Generates query filters for 'Condition' objects based on the current date and time.

    Returns two query filter:
    - for_datetime: Filters for conditions either scheduled for a date earlier
                    than today or for today with a time earlier than or equal
                    to the current time, and not finished.

    :return: A tuple containing two query filters (for_date, for_datetime).
    """

    current_date = timezone.now().date()
    current_time = timezone.now().time()

    for_datetime = (Q(condition__scheduled_date=current_date, condition__scheduled_time__lte=current_time) |
                    Q(condition__scheduled_date__lt=current_date, condition__scheduled_time__isnull=False)
                    ) & Q(condition__finished=False)

    return for_datetime


def queryset_with_filter_condition(for_datetime: Q) -> bool:
    """
    Evaluates whether there are any Mother objects that match the given query filters.
    """
    exists_for_datetime = Mother.objects.filter(for_datetime).exists()
    return exists_for_datetime


def is_filtered_condition_met(previous_url: str, for_datetime: bool) -> bool:
    """
    Checks if the previous URL is a filtered condition and if the respective queryset is not empty.
    """

    if previous_url:
        not_filtered_list_page = previous_url.endswith('by_date_and_time')
        previous_url_without_filtered_change_list = previous_url and not not_filtered_list_page

        if previous_url_without_filtered_change_list:
            return True
        if previous_url.endswith('by_date_and_time') and for_datetime:
            return True
        return False


def redirect_to_appropriate_url(request: HttpRequest, previous_url: str, default_url: str) -> HttpResponseRedirect:
    """
    Redirects to the appropriate URL based on the previous URL or defaults to the provided URL.
    """
    if previous_url:
        del request.session['previous_url']
        return HttpResponseRedirect(previous_url)
    return HttpResponseRedirect(default_url)


def render_icon(is_success: bool) -> str:
    """
    Render green icon if True else red icon
    """
    icon_color = 'green' if is_success else 'red'
    icon_path = static(f'mothers/icons/{icon_color}_check_mark.jpg')
    return mark_safe(
        f'<img src="{icon_path}" alt="{"Success" if is_success else "Failure"}" style="width: 20px; height: 20px;"/>'
    )


def format_date_or_time(value: Union[date, time]) -> str:
    """
    Return various string format based on date time type
    """
    if isinstance(value, date):
        return formats.date_format(value, "j M Y")
    elif isinstance(value, time):
        return formats.date_format(value, "H:i")


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


def validate_time_date_dependencies(form: ConditionAdminForm, cleaned_data: Dict[str, Any]) -> None:
    """
    Ensures that if a time is set, a date must also be set, and vice versa.
    """
    scheduled_date, scheduled_time, _, _ = cleaned_date_time_and_condition(cleaned_data)

    if scheduled_time and not scheduled_date:
        form.add_error('scheduled_date', "Date must be provided if time is set.")
    if scheduled_date and not scheduled_time:
        form.add_error('scheduled_time', "Time must be provided if date is set.")


def validate_condition_with_date(form: ConditionAdminForm, cleaned_data: Dict[str, Any]) -> None:
    """
    Checks conditions that require a date and adds an error if a date is not provided.
    """
    condition_has_date = ['no baby', 'WWW']  # list of states which must have scheduled date
    scheduled_date, scheduled_time, condition, _ = cleaned_date_time_and_condition(cleaned_data)
    if condition in condition_has_date and not (scheduled_date and scheduled_time):
        form.add_error('condition', "Date and Time must be provided if this state is set.")


def validate_empty_condition(form: ConditionAdminForm, cleaned_data: Dict[str, Any]) -> None:
    """
    Checks reason exists if condition is empty.
    """
    _, _, condition, reason = cleaned_date_time_and_condition(cleaned_data)
    empty_condition = condition is None or condition == Condition.ConditionChoices.__empty__

    if empty_condition and not reason:
        form.add_error('reason', "Specify understandable reason for empty state")


def validate_reason_has_datetime(form: ConditionAdminForm, cleaned_data: Dict[str, Any]) -> None:
    """
    Checks reason has date and time.
    """
    scheduled_date, scheduled_time, condition, reason = cleaned_date_time_and_condition(cleaned_data)

    if condition is None and reason and not scheduled_date:
        form.add_error('scheduled_date', "Specify date")
    if condition is None and reason and not scheduled_date:
        form.add_error('scheduled_time', "Specify time")


def if_field_error_exists(form: ConditionAdminForm, cleaned_data: Dict[str, Any]) -> None:
    """
    Finally, if from only single method error exists, then break validation and error display at the top of the field.
    """
    errors = form.errors
    functions = [
        validate_time_date_dependencies,
        validate_condition_with_date,
        validate_empty_condition,
        validate_reason_has_datetime,
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


def hide_mother_field_on_add(form: ConditionAdminForm) -> None:
    """
    Hides the mother field if this is a new instance (i.e., not yet saved in the database).
    """
    if not form.instance.pk:
        form.fields['mother'].widget = forms.HiddenInput()


def set_initial_mother_value_on_add(form: ConditionAdminForm, request: Optional[HttpRequest]) -> None:
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

    :param db_field: The database field from which to extract choices.
    :return: A list of choice tuples.
    """
    return db_field.get_choices(include_blank=db_field.blank, blank_choice=[('', '---------')])


def is_add_action(obj: Condition) -> bool:
    """
    Determines whether the current action is 'add'.

    :return: True if it's an 'add' action, False otherwise.
    """
    return not (obj and obj.pk)


def filter_choices(obj: Condition, request: HttpRequest, choices: List[Tuple[Any, Any]]) -> List[Tuple[Any, Any]]:
    """
    Filters choices based on the action type (add or change).

    :param choices: The original list of choice tuples.
    :param is_add_action: A boolean indicating whether the action is 'add' (True) or 'change' (False).
    :return: A list of filtered choice tuples.
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


def convert_to_utc_and_save(request: HttpRequest, obj: Condition) -> None:
    """
    Converts the scheduled date and time from the user's local timezone to UTC.
    """
    from mothers.services.mother import convert_local_to_utc

    if obj.scheduled_date and obj.scheduled_time:
        utc_aware_datetime = convert_local_to_utc(request, obj)
        obj.scheduled_date = utc_aware_datetime.date()
        obj.scheduled_time = utc_aware_datetime.time()


def assign_permissions_to_user(user: User, obj: Condition) -> None:
    """
    Assigns 'view_condition' and 'change_condition' permissions to the user for the given Condition instance.
    """
    # Retrieve or define the user to whom permissions will be assigned
    username = user.username
    user_primary_stage = User.objects.get(username=username)

    # Assign permission for each new instance of Condition
    assign_perm('view_condition', user_primary_stage, obj)
    assign_perm('change_condition', user_primary_stage, obj)


def has_permission(adm: ModelAdmin, request: HttpRequest, obj: Condition, action: str, base_permission) -> bool:
    """
    Checks if the user has the specified permission for the given object. If the user has model lvl permission,
    or if the user has the specific permission on the object, it returns True.
    If the object is not specified, always return False
    """
    _meta = adm.opts
    code_name = f'{action}_{_meta.model_name}'
    if obj:
        return request.user.has_perm(f'{_meta.app_label}.{code_name}', obj) \
            or request.user.has_perm(f'{_meta.app_label}.{code_name}')  # in this case add user only view perm

    if base_permission:
        return False


def adjust_button_visibility(context: Dict[str, Any], add: bool, change: bool) -> None:
    """
    Adjusts the visibility of form buttons in the admin change form context.
    """
    # If we are adding a new instance (not changing), adjust the visibility of buttons.
    if add or change:
        context['show_save_and_add_another'] = False  # Remove "Save and add another" button
        context['show_save_and_continue'] = False  # Remove "Save and continue editing" button
        context['show_save'] = True  # Ensure "Save" button is visible


def after_add_message(self: ModelAdmin, request: HttpRequest, obj: Condition) -> None:
    url = reverse('admin:mothers_mother_change', args=[obj.mother.id])
    message = format_html(
        f'Condition "<strong>{obj.get_condition_display()}</strong>" '
        f'successfully created for <a href="{url}">{obj.mother}</a>'
    )
    self.message_user(request, message, messages.SUCCESS)


def after_change_message(self: ModelAdmin, request: HttpRequest, obj: Condition) -> None:
    url = reverse('admin:mothers_mother_change', args=[obj.mother.id])

    if obj.finished:
        message = format_html(
            f'Condition "<strong>{obj.get_condition_display()}</strong>"'
            f' already completed for <a href="{url}">{obj.mother}</a>'
        )
        self.message_user(request, message, messages.SUCCESS)
