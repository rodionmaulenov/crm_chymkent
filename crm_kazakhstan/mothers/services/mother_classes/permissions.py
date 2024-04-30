from abc import ABC, abstractmethod
from guardian.shortcuts import get_objects_for_user

from django.contrib.admin import ModelAdmin
from django.urls import reverse_lazy
from django.http import HttpRequest
from django.db.models import QuerySet
from django.db import models

from mothers.models import Mother


class PermissionConstruct(ABC):
    def __init__(self, admin: ModelAdmin, request: HttpRequest, action: str = None):
        self.admin = admin
        self.request = request
        self.action = action
        self.user = request.user
        self._meta = admin.opts
        self.app = self._meta.app_label
        self.model = self._meta.model_name

    @property
    def users_name(self):
        return self.user.username

    @property
    def users_stage(self):
        return self.user.stage

    def users_permission(self, permission: str, obj: models.Model = None) -> bool:
        return self.user.has_perm(permission, obj)

    @property
    def base_permission(self) -> str:
        """User`s base permission."""
        return f'{self.app}.{self.action}_{self.model}'

    @property
    def custom_permission(self) -> str:
        """User`s custom permission."""
        return f'{self.users_stage}_{self.model}_{self.users_name}'.lower()


class CheckData(PermissionConstruct):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.klass = self._meta.model

    def users_assign_objs(self) -> QuerySet:
        """
        Retrieves a QuerySet of objects from the model associated with the provided ModelAdmin instance (`adm`).
        The objects are filtered based on the user's permissions. It checks if the user has custom permissions
        for the objects of the model.
        Super-user gets all queryset.
        """
        # Retrieve and return the objects for which the user has the specified permissions
        return get_objects_for_user(user=self.user, perms=self.custom_permission, klass=self.klass)

    def filter_data(self, custom_filter=None) -> QuerySet:
        return custom_filter(self.users_assign_objs()) if custom_filter is not None else self.users_assign_objs()

    def users_query_exists(self, custom_filter=None) -> bool:
        """If exists queryset data."""
        return self.filter_data(custom_filter).exists()

    @abstractmethod
    def has_permission(self, *args, **kwargs):
        pass


class ModuleLevel(CheckData):
    def has_permission(self, base, custom_filter=None) -> bool:
        """Check cases where the user has a base permission
        or queryset of objects belonging to the administrator class."""
        if not self.user.is_authenticated:
            return False

        users_data = self.users_query_exists(custom_filter)
        return users_data or base


class ObjectListLevel(CheckData):
    def has_permission(self, custom_filter=None, obj: Mother = None) -> bool:
        """
            If obj:
              Base permission or custom permission previously assigned to this object.
            list level:
              The base permission or query set owned by the user.
        """

        base = self.users_permission(self.base_permission)

        match obj:
            case None:
                users_data = self.users_query_exists(custom_filter)
                return users_data or base
            case _:
                custom = self.users_permission(self.custom_permission, obj)
                return custom or base


class ObjectLevel(CheckData):
    def has_permission(self, obj: Mother = None) -> bool:
        """
            If obj:
              Base permission or custom permission previously assigned to this object.
            list level:
              False.
        """

        base = self.users_permission(self.base_permission)
        custom = self.users_permission(self.custom_permission, obj)
        return custom or base if obj is not None else False


class WrappedUrlObjectList(ObjectListLevel):
    def has_permission(self, custom_filter=None, obj: Mother = None) -> bool:
        """
        At the object level:
        - When the user has basic permission or when the user is assigned an object.
        List level:
        - Basic permission is when the user has or when the user has objects assigned to him.
        """
        url = reverse_lazy('admin:mothers_mother_changelist')
        if str(url) in self.request.path:
            return super().has_permission(custom_filter, obj)
        return False


class PermissionCheckerFactory:
    @staticmethod
    def get_checker(admin: ModelAdmin, request: HttpRequest, class_name: str, action: str = None):
        """
        Factory method that dynamically returns an instance of the specified
        permission checker class based on the class name.
        """
        permission_checker_class = globals().get(class_name)

        if permission_checker_class and issubclass(permission_checker_class, PermissionConstruct):
            return permission_checker_class(admin, request, action)
        else:
            raise ValueError(f'No valid permission checker class found for name: {class_name}')
