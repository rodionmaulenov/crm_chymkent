from django.forms.widgets import ClearableFileInput
from django import forms


class CustomFileInput(ClearableFileInput):
    template_name = 'custom_widgets/custom_file_input.html'

    class Media:
        js = ('custom_widgets/js/custom_file_input.js',)
        css = {
            'all': ('custom_widgets/css/custom_file_input.css',)
        }


class CustomSelectWidget(forms.Select):
    template_name = 'custom_widgets/custom_select_widget.html'

    class Media:
        css = {
            'all': ('custom_widgets/css/custom_select_widget.css',)
        }
