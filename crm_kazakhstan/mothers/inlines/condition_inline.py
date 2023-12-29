"""
This class create condition states for mothers in different termsThe ConditionInline class is a custom inline admin for the Condition model in a Django application. It allows Condition instances to be edited inline on the Mother model's admin change page. Here's a detailed description of its functionality and the customizations made:
Description of ConditionInline:

    Model Association: The inline is associated with the Condition model, which seems to be related to a Mother model via a foreign key.
    Formset Customization: It uses a custom formset class, CustomConditionInlineFormset, to handle the creation and rendering of forms for Condition instances.
    Form Customization: The inline specifies ConditionInlineFormWithoutFinished as the form to use when rendering each Condition instance. This form includes custom logic to handle instances differently based on their finished state.
    Maximum Number of Forms: The max_num property is initially set to 1, indicating that only one empty form should be displayed by default for adding a new Condition. This value may be increased dynamically based on certain conditions.

Custom Code and Overriding:

    CustomConditionInlineFormset:
        Overrides the __init__ method to set the initial values for scheduled_date and scheduled_time fields based on the user's timezone.
        The _construct_form method is overridden to customize the field rendering. For each form in the formset, if the associated Condition instance is marked as finished, the form fields are wrapped with EmptyOnlyFieldWrapper to display a span with 'empty' or the actual value instead of the default form widget. This is particularly applied to the scheduled_date, scheduled_time, and condition fields.

    ConditionInlineFormWithoutFinished:
        In its __init__ method, if the Condition instance is finished, all form fields are disabled, making them read-only.
        The clean method includes custom validation logic to ensure that if a scheduled_time is provided, a scheduled_date must also be set.

    get_formset Method in ConditionInline:
        Overridden to provide custom logic for determining the max_num of inline forms. It increases the max_num by 1 if there are existing Condition instances related to the mother that are marked as finished, and certain time-based conditions (time = by_date_or_by_datatime(request)) are not met.

Usage in Admin Interface:

This inline admin configuration allows users to view and edit Condition instances directly from the Mother instance's admin page. It handles different states of Condition instances and presents them accordingly, providing a user-friendly and context-aware interface for managing related data. The custom formset and form ensure that the admin interface behaves as expected when dealing with Condition instances, taking into account the time zone of the user and the finished state of the conditions.
"""

from django.contrib import admin
from django.forms import BaseInlineFormSet
from django import forms
from django.utils.html import format_html

from mothers.constants import CONDITION_CHOICES
from mothers.services import convert_utc_to_local, by_date_or_by_datatime
from mothers.models import Condition


class EmptyOnlyFieldWrapper:
    """
    This class exists only for pre-populate form that will render "empty" string if field blank,
    or the actual value in a span for specific fields when instance.finished is True.
    """

    def __init__(self, widget, field_name=None, finished=False):
        self.original_widget = widget
        self.field_name = field_name
        self.finished = finished

    def render(self, name, value, attrs=None, renderer=None):

        if self.finished and self.field_name in ['scheduled_date', 'scheduled_time']:
            return format_html('<span>{}</span>', value or 'empty')

        elif self.finished and self.field_name == 'condition':
            long_description = dict(CONDITION_CHOICES).get(value)
            return format_html('<span>{}</span>', long_description)

        elif value:
            return self.original_widget.render(name, value, attrs, renderer)

        else:
            return format_html('<span>{}</span>', 'empty')

    @property
    def needs_multipart_form(self):
        return self.original_widget.needs_multipart_form

    @property
    def is_hidden(self):
        return self.original_widget.is_hidden

    @property
    def use_required_attribute(self):
        return self.original_widget.use_required_attribute

    @property
    def attrs(self):
        return self.original_widget.attrs

    @property
    def value_from_datadict(self):
        return self.original_widget.value_from_datadict

    @property
    def supports_microseconds(self):
        # Delegate the supports_microseconds to the original widget
        return getattr(self.original_widget, 'supports_microseconds', False)


class ConditionInlineFormWithoutFinished(forms.ModelForm):
    class Meta:
        model = Condition
        fields = ('condition', 'reason', 'scheduled_date', 'scheduled_time')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        finished = self.instance.finished if self.instance else False

        # If finished = True instance stand be not changeable
        if finished:
            for field in self.fields:
                self.fields[field].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        scheduled_time = cleaned_data.get("scheduled_time")
        scheduled_date = cleaned_data.get("scheduled_date")

        if scheduled_time and not scheduled_date:
            self.add_error('scheduled_date', "Date must be provided if time is set.")

        return cleaned_data


class ConditionInlineFormWithFinished(ConditionInlineFormWithoutFinished):
    class Meta:
        model = Condition
        fields = '__all__'


class CustomConditionInlineFormset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            if form.instance.pk:
                user_timezone = getattr(self.request.user, 'timezone', 'UTC')
                utc_date = form.instance.scheduled_date
                utc_time = form.instance.scheduled_time
                if utc_date and utc_time:
                    # Convert UTC date and time to user's local timezone
                    local_datetime = convert_utc_to_local(utc_date, utc_time, user_timezone)
                    # Update the initial time of the form
                    form.initial['scheduled_time'] = local_datetime.time()
                    form.initial['scheduled_date'] = local_datetime.date()

    def _construct_form(self, i, **kwargs):
        """
        Customizes field rendering for special fields when the instance is finished.
        """
        form = super()._construct_form(i, **kwargs)
        finished = form.instance.finished if form.instance else False

        for field_name, field_inst in form.fields.items():
            if field_name not in ['finished', 'DELETE']:
                is_special_field = field_name in ['scheduled_date', 'scheduled_time', 'condition']
                form.fields[field_name].widget = EmptyOnlyFieldWrapper(
                    field_inst.widget,
                    field_name=field_name,
                    finished=finished and is_special_field
                )

        return form


class ConditionInline(admin.TabularInline):
    model = Condition
    extra = 0
    formset = CustomConditionInlineFormset
    form = ConditionInlineFormWithoutFinished
    max_num = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset_class = super().get_formset(request, obj, **kwargs)

        # increase max_num by 1 if mother instance from changelist url
        res = obj.condition_set.filter(finished=True).count()
        time = by_date_or_by_datatime(request)
        if res >= 0 and not time:
            formset_class.max_num = res + 1

        formset_class.request = request
        return formset_class
