from abc import ABC, abstractmethod

from django.urls import reverse_lazy
from django.contrib.admin import ModelAdmin
from django.http import HttpRequest
from django.db.models import QuerySet
from django.db import models

from mothers.models import Mother
from mothers.services.mother import get_model_objects

MOTHERS_CHANGE_LIST_URL = reverse_lazy('admin:mothers_mother_changelist')


class PermissionChecker(ABC):
    def __init__(self, admin: ModelAdmin, request: HttpRequest):
        self.admin = admin
        self.request = request
        self.user = request.user
        self._meta = admin.opts
        self.app = self._meta.app_label
        self.model = self._meta.model_name

    def has_base_permission(self, action: str) -> bool:
        """
        Check if the user has the base permission for the given action.
        """
        base_perm = f'{self.app}.{action}_{self.model}'
        return self.user.has_perm(base_perm)

    def has_custom_permission(self, obj: models = None) -> bool:
        """
        Check if the user has a custom permission for the given object.
        """
        username = self.user.username
        stage = self.user.stage
        custom_perm = f'{stage}_{self.model}_{username}'.lower()
        return self.user.has_perm(custom_perm, obj)

    @abstractmethod
    def has_permission(self, *args, obj: models = None):
        action = args[0]
        func = None
        if len(args) > 1:
            func = args[1]
        return action, func


class CheckData:
    @property
    def model_objects(self) -> QuerySet:
        """
        Get objects owned to user.
        """
        return get_model_objects(self.admin, self.request)

    def filtered_data(self, func=None) -> QuerySet:
        """
        Add custom filter.
        """
        data = func(self.model_objects) if func is not None else self.model_objects
        return data

    def data_exists(self, func=None) -> bool:
        """
        Verify if data exists.
        """
        return self.filtered_data(func).exists()


class ModulePermission(PermissionChecker, CheckData):

    def has_permission(self, *args, obj: Mother = None) -> bool:
        """
        Basic permission is when the user has or when the user has objects assigned to him.
        """
        base, func = super().has_permission(*args, obj=obj)

        if not self.user.is_authenticated:
            return False

        users_data = self.data_exists(func)
        return users_data or base


class ObjectListLevelPermission(PermissionChecker, CheckData):

    def has_permission(self, *args, obj: Mother = None) -> bool:
        """
        At the object level:
        - When the user has basic permission or when the user is assigned an object.
        List level:
        - Basic permission is when the user has or when the user has objects assigned to him.
        """
        action, func = super().has_permission(*args, obj=obj)

        base = self.has_base_permission(action)
        custom = self.has_custom_permission(obj)

        if obj is not None:
            return custom or base

        users_data = self.data_exists(func)
        return users_data or base


class ObjectLevelPermission(PermissionChecker, CheckData):

    def has_permission(self, *args, obj: Mother = None) -> bool:
        """
        At the object level:
        - When the user has basic permission or when the user is assigned an object.
        List level:
        - Always False.
        """
        action, func = super().has_permission(*args, obj=obj)

        base = self.has_base_permission(action)
        custom = self.has_custom_permission(obj)

        if obj is not None:
            return custom or base

        return False


class BasedOnUrlChangePermission(ObjectListLevelPermission):

    def has_permission(self, *args, obj: Mother = None) -> bool:
        """
        At the object level:
        - When the user has basic permission or when the user is assigned an object.
        List level:
        - Basic permission is when the user has or when the user has objects assigned to him.
        """

        if str(MOTHERS_CHANGE_LIST_URL) in self.request.path:
            return super().has_permission(*args, obj=obj)
        return False


class PermissionCheckerFactory:
    @staticmethod
    def get_checker(admin: ModelAdmin, request: HttpRequest, class_name: str):
        """
        Factory method that dynamically returns an instance of the specified
        permission checker class based on the class name.
        """
        permission_checker_class = globals().get(class_name)

        if permission_checker_class and issubclass(permission_checker_class, PermissionChecker):
            return permission_checker_class(admin, request)
        else:
            raise ValueError(f'No valid permission checker class found for name: {class_name}')
