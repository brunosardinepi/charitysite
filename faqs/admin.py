from django.contrib import admin

from . import models


class FAQAdmin(admin.ModelAdmin):
    list_display = ('order', 'question',)
    ordering = list_display

admin.site.register(models.FAQ, FAQAdmin)
