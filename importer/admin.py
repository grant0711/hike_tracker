from django.contrib import admin
from django_admin_inline_paginator.admin import TabularInlinePaginated

from .models import Hike, TrackPoint


class TrackPointInline(TabularInlinePaginated):
    model = TrackPoint
    fields = ('isof_datetime', 'lat', 'lon', 'heart_rate')
    readonly_fields = ('isof_datetime', 'lat', 'lon', 'heart_rate')
    ordering = ('datetime',)
    per_page = 20
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description='Datetime (ISO)', ordering='datetime')
    def isof_datetime(self, obj):
        if obj.datetime:
            return obj.datetime.isoformat()
        return None

class HikeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    inlines = (TrackPointInline,)
    fields = ('name', 'description')

admin.site.register(Hike, HikeAdmin)
