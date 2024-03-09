from typing import Optional, Tuple, Dict, Any

from django.contrib import admin
from django.http import HttpRequest
from django.db.models import QuerySet
from django.forms import ModelForm
from django.contrib.admin.helpers import AdminForm

from mothers.admin import MotherAdmin
from mothers.forms import BanAdminForm
from mothers.models import Ban, Mother
from mothers.services.ban import view_perm, add_perm, on_ban_stage
from mothers.services.mother import get_model_objects
from mothers.services.state import adjust_button_visibility, assign_permissions_to_user


@admin.register(Ban)
class BanAdmin(admin.ModelAdmin):
    form = BanAdminForm
    fields = ('mother', 'comment', 'banned')
    readonly_fields = ('mother',)

    def get_fields(self, request: HttpRequest, obj: Optional[Ban] = None) -> Tuple[str, ...]:
        """
        Define which fields to display on the add and change forms.
        """
        if obj is None:
            return 'mother', 'comment'
        else:
            return 'mother', 'comment'

    def get_readonly_fields(self, request: HttpRequest, obj=None) -> Tuple[str, ...]:
        """
        Determine the readonly fields based on whether an object is being added or changed.
        """
        if obj:  # This is the change page
            return self.readonly_fields
        else:  # This is the add page
            return ()

    def render_change_form(self, request: HttpRequest, context: Dict[str, Any],
                           add: bool = False, change: bool = False,
                           form_url: str = '', obj: Optional[Ban] = None) -> AdminForm:
        """
        Override the method to modify the context for the change form template.

        This method is called before the admin form is rendered and allows us to
        alter the context dictionary that is passed to the template. The visibility
        of the "Save and add another" and "Save and continue editing" buttons is
        controlled based on whether a new instance is being added or an existing
        instance is being changed.
        """

        adjust_button_visibility(context, add, change)

        # Render the change form with the adjusted context
        return super().render_change_form(request, context, add=add, change=change,
                                          form_url=form_url, obj=obj)

    def save_model(self, request: HttpRequest, obj: Ban, form: ModelForm, change: bool) -> None:
        """
        Handles the saving of a Ban instance in the Django admin interface.
        Assigns permissions if it's a new instance.
        """
        is_new = not obj.pk  # Check if the object is new (has no primary key yet)

        super().save_model(request, obj, form, change)

        if is_new:
            # Assign permission for each new instance of Condition
            assign_permissions_to_user(request.user, obj, ['view_ban'])

    def has_module_permission(self, request: HttpRequest) -> bool:
        """
        Permission for first layer on site, see or not Mother. If superuser True else objects that has the same
        with user perms exist or not.
        """
        mother_admin = MotherAdmin(Mother, admin.site)
        users_objs = get_model_objects(mother_admin, request, ['view', 'change']).exists()

        base = super().has_module_permission(request)
        return base or users_objs

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """
        Queryset contains exclusively the Mother instances where Stage is Ban
        """
        # assign request for using in custom MotherAdmin methods
        self.request = request

        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'mother'
        )
        if request.user.has_perm('mothers.view_ban'):
            return queryset

        data = get_model_objects(self, request)
        data = on_ban_stage(data)
        return data

    def has_view_permission(self, request: HttpRequest, obj: Ban = None) -> bool:
        return view_perm(self, request, obj, 'view')

    def has_add_permission(self, request: HttpRequest) -> bool:
        add = super().has_add_permission(request)
        return add_perm(request, add)

    # def response_add(self, request: HttpRequest, obj: Ban, post_url_continue=None) -> HttpResponseRedirect:
    #     """After add redirect ot mother changelist page."""
    #
    #     mother_changelist = reverse('admin:mothers_mother_changelist')
    #     self.message_user(request, after_add_message(obj), level=messages.SUCCESS)
    #     return HttpResponseRedirect(mother_changelist)