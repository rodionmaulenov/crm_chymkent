from django.forms.widgets import ClearableFileInput


class CustomTextArea(ClearableFileInput):
    template_name = 'widgets/resize_textarea.html'

    class Media:
        css = {
            'all': ('widgets/css/resize_textarea.css',)
        }
