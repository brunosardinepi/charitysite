from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from . import models


class PageAdmin(GuardedModelAdmin):
    list_display = ('id', 'name', 'page_slug', 'category',)
    ordering = ('id', 'name', 'page_slug',)
    list_filter = ('category',)
    filter_horizontal = ('admins', 'managers',)

admin.site.register(models.Page, PageAdmin)
