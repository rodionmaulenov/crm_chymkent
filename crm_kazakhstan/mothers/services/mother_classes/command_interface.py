import pytz

from typing import Optional, List
from datetime import datetime

from django.urls import reverse_lazy
from django.contrib.admin import ModelAdmin
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import redirect
from django.utils.html import format_html
from django.contrib import messages
from django.db.models import QuerySet

from mothers.models import Stage, Ban, Mother
from mothers.services.mother import redirect_to, simple_redirect, convert_utc_to_local
from mothers.services.mother_classes.formatter_interface import BoldDayMonthYearHourMinuteFormatter


# Command Interface
class Command:
    def execute(self, *args, **kwargs):
        raise NotImplementedError("You should implement this method.")


# Concrete Command
class MoveToBanCommand(Command):
    _MOTHER_CHANGELIST_URL = reverse_lazy('admin:mothers_mother_changelist')
    _MOTHER_ADD_URL = reverse_lazy('admin:mothers_ban_add')
    _related_exists: Optional[str] = None

    @classmethod
    def check_queryset(cls, request, queryset: QuerySet):
        """Previously check that mother must be only one."""
        if queryset.count() != 1:
            message = 'Please choose exactly one instance'
            return simple_redirect(request, cls._MOTHER_CHANGELIST_URL, message, messages.INFO)

    def __init__(self, request, queryset):
        self.request = request
        self.http_redirect = self.check_queryset(request, queryset)
        self.mother = self.http_redirect if isinstance(self.http_redirect, HttpResponseRedirect) else queryset.first()

    @property
    def foreign_model(self):
        return self.if_exists(self.mother)

    def if_exists(self, mother):
        """Verify if mothers related objects exist."""
        if mother.state.exists() or mother.plan.exists():
            message = f'<b>{mother}</b> has no finished action'
            return simple_redirect(self.request, self._MOTHER_CHANGELIST_URL, message, messages.INFO)

    def execute(self, *args, **kwargs):
        """Redirect on add Ban page."""
        if isinstance(self.mother, HttpResponseRedirect):
            return self.http_redirect

        if isinstance(self.foreign_model, HttpResponseRedirect):
            return self.foreign_model
        else:
            # Add the mother's ID as a query parameter
            add_url = f"{self._MOTHER_ADD_URL}?mother={self.mother.pk}"
            return HttpResponseRedirect(add_url)


class ResponseAddBanCommand(Command):
    def __init__(self, request: HttpRequest, obj: Ban, path: dict, post_url_continue=None):
        self.request = request
        self.obj = obj
        self.post_url_continue = post_url_continue
        self.path = path

    @property
    def get_mother(self):
        return self.obj.mother

    def end_stage(self):
        stage = self.get_mother.stage_set.filter(finished=False).first()
        stage.finished = True
        stage.save()

    def end_ban(self):
        self.obj.banned = True
        self.obj.save()

    def proceed_stage(self, stage):
        new_stage = Stage(mother=self.get_mother, stage=stage, finished=False)
        new_stage.save()

    def execute(self, text=None, message_state=None):
        """The mother has been assigned a different state and the previous one has been completed."""
        self.end_stage()
        self.end_ban()

        self.proceed_stage(Stage.StageChoices.BAN)

        return redirect_to(self.request, self.obj, text, self.path, message_state)


class ScheduledDateTimeCommand(Command):
    _format = None

    def __init__(self, request: HttpRequest, obj: Mother):
        self.request = request
        self.obj = obj

    @property
    def is_state(self):
        return self.obj.state.exists()

    @property
    def state(self):
        return self.obj.state.first()

    def formated_time(self, local_time):
        formatter = BoldDayMonthYearHourMinuteFormatter()
        self._format = formatter.format(local_time)

    def execute(self, *args, **kwargs):
        """Getting user local time in specified format."""
        if self.is_state:
            local_time = convert_utc_to_local(self.request, self.state.scheduled_date, self.state.scheduled_time)
            self.formated_time(local_time)

        return self._format


class WhenCreatedCommand(Command):

    def __init__(self, request: HttpRequest, obj: Mother):
        self.request = request
        self.obj = obj

    @property
    def users_timezone(self):
        """
        Returns the current datetime object in the user's timezone. Defaults to UTC if the user's timezone is not set.
        """
        timezone_str = getattr(self.request.user, 'timezone', 'UTC')
        timezone = pytz.timezone(str(timezone_str))
        return datetime.now(timezone)

    @staticmethod
    def formated_time(local_time):
        formatter = BoldDayMonthYearHourMinuteFormatter()
        return formatter.format(local_time)

    def execute(self, *args, **kwargs):
        """Turns UTC time into the local user time."""
        return self.formated_time(self.users_timezone)


class FromBanCommand(Command):
    _mother_changelist = reverse_lazy('admin:mothers_mother_changelist')

    def __init__(self, admin: ModelAdmin, request: HttpRequest, queryset: List[Mother]):
        self.admin = admin
        self.request = request
        self.queryset = queryset

    def add_message(self, mother):
        self.admin.message_user(
            self.request,
            format_html(f'<b>{mother}</b> has successfully returned from ban'),
            messages.SUCCESS,
        )

    @staticmethod
    def add_new_stage(mother):
        new_stage = Stage(mother=mother, stage=Stage.StageChoices.PRIMARY, finished=False)
        new_stage.save()

    def end_ban_stage(self):
        for mother in self.queryset:
            stage = mother.stage_set.filter(finished=False).first()
            stage.finished = True
            stage.save()

            self.add_new_stage(mother)
            self.add_message(mother)

    def execute(self) -> redirect:
        self.end_ban_stage()

        return redirect(self._mother_changelist)
