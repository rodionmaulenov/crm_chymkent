from typing import Optional, Dict, Any

from django.contrib import admin, messages
from django.contrib.admin.helpers import AdminForm
from django.forms import ModelForm
from django.urls import reverse
from django.http import HttpRequest, HttpResponseRedirect
from django.db.models import QuerySet

from documents.models import MainDocument

from gmail_messages.services.manager_factory import ManagerFactory

from mothers.admin import MotherAdmin
from mothers.models import Mother
from mothers.services.mother import redirect_to
from mothers.services.mother_classes.permissions import PermissionCheckerFactory
from mothers.services.state import adjust_button_visibility


@admin.register(MainDocument)
class DocumentAdmin(admin.ModelAdmin):
    fields = ('mother', 'kind', 'title', 'note', 'file')

    # def render_change_form(self, request: HttpRequest, context: Dict[str, Any],
    #                        add: bool = False, change: bool = False,
    #                        form_url: str = '', obj: Optional[Document] = None) -> AdminForm:
    #     """
    #     Override the method to modify the context for the change form template.
    #
    #     This method is called before the admin form is rendered and allows us to
    #     alter the context dictionary that is passed to the template. The visibility
    #     of the "Save and add another" and "Save and continue editing" buttons is
    #     controlled based on whether a new instance is being added or an existing
    #     instance is being changed.
    #     """
    #
    #     adjust_button_visibility(context, add, change)
    #
    #     # Render the change form with the adjusted context
    #     return super().render_change_form(request, context, add=add, change=change,
    #                                       form_url=form_url, obj=obj)

    def save_model(self, request: HttpRequest, obj: MainDocument, form: ModelForm, change: bool) -> None:
        """
        Handles the saving of a Ban instance in the Django admin interface.
        Assigns permissions if it's a new instance.
        """
        is_new = not obj.pk  # Check if the object is new (has no primary key yet)
        super().save_model(request, obj, form, change)

        if is_new:
            # Assign permission for each new instance of Condition
            user = request.user

            factory = ManagerFactory()
            primary_manager = factory.create('PrimaryStageManager')
            primary_manager.assign_user(content_type=self, obj=obj, user=user)

    def has_module_permission(self, request: HttpRequest) -> bool:
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        self.request = request
        return super().get_queryset(request)

    # def has_view_permission(self, request: HttpRequest, document: Document = None) -> bool:
    #     # delete
    #     class_name = 'ObjectLevel'
    #     permission_checker = PermissionCheckerFactory.get_checker(self, request, class_name, 'view')
    #     has_perm = permission_checker.has_permission(obj=document)
    #     return has_perm
    #
    # def has_change_permission(self, request, obj=None):
    #     # delete
    #     return True
    #
    # def has_add_permission(self, request: HttpRequest, document: Document = None) -> bool:
    #     # delete
    #     base = super().has_add_permission(request)
    #
    #     mother_admin = MotherAdmin(Mother, admin.site)
    #     class_name = 'ModuleLevel'
    #     permission_checker = PermissionCheckerFactory.get_checker(mother_admin, request, class_name)
    #     has_perm = permission_checker.has_permission(base)
    #     return has_perm

    # def response_add(self, request: HttpRequest, obj: Document, post_url_continue=None) -> HttpResponseRedirect:
    #     # delete
    #     """
    #     After add redirect on document proxy change list.
    #
    #     As well if changelist has been filtered before add statement,
    #     it redirects on this filtered change list page.
    #     """
    #     path_dict = {
    #         'message_url': reverse('admin:mothers_mother_change', args=[obj.mother.id]),
    #         'base_url': reverse('admin:documents_documentproxy_changelist')
    #     }
    #     text = f'{obj}, successfully added for'
    #     return redirect_to(request, obj, text, path_dict, messages.SUCCESS)
