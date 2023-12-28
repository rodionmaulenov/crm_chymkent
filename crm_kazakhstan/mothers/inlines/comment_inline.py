from django.contrib import admin

from mothers.models import Comment


class CommentInline(admin.TabularInline):
    model = Comment
    fields = ('description',)
    extra = 0
