"""
This class create condition states for mothers in different terms
"""

from django.contrib import admin
from django.forms import BaseInlineFormSet
from django import forms
from django.utils.html import format_html

from mothers.services import convert_utc_to_local, by_date_or_by_datatime
from mothers.models import Condition


class EmptyOnlyFieldWrapper:
    """
    This class exists only for pre-populate form that will render "empty" string if field blank
    """

    def __init__(self, widget):
        self.original_widget = widget

    def render(self, name, value, attrs=None, renderer=None):
        if value:
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


class ConditionInlineFormWithoutFinished(forms.ModelForm):
    class Meta:
        model = Condition
        fields = ('condition', 'reason', 'scheduled_date', 'scheduled_time')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If finished = True instance stand be not changeable
        instance = kwargs.get('instance')
        if instance and instance.finished:
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
        Fills empty fields by string 'emtpy'
        """
        form = super()._construct_form(i, **kwargs)
        if form.instance.pk:  # Check if the instance is saved
            for field_name, field in form.fields.items():
                if not form.initial.get(field_name) and field_name != 'finished' and field_name != 'DELETE':
                    form.fields[field_name].widget = EmptyOnlyFieldWrapper(field.widget)
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
