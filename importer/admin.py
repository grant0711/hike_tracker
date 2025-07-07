from django.contrib import admin
from django_admin_inline_paginator.admin import TabularInlinePaginated
from django.db.models import Min, Max

from .models import Hike, TrackPoint


class TrackPointInline(TabularInlinePaginated):
    model = TrackPoint
    ordering = ('datetime',)
    per_page = 20
    can_delete = False
    fields = ('isof_datetime', 'lat', 'lon', 'heart_rate')
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        return self.fields

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


    @admin.display(description='Datetime (ISO)', ordering='datetime')
    def isof_datetime(self, obj):
        if obj.datetime:
            return obj.datetime.isoformat()
        return None

class HikeAdmin(admin.ModelAdmin):
    list_display = ("name", "get_date", "get_duration")
    inlines = (TrackPointInline,)
    fields = ('name', 'description')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            start_time=Min('points__datetime'),
            end_time=Max('points__datetime')
        )
        return queryset

    @admin.display(description='Date', ordering='start_time')
    def get_date(self, obj):
        if obj.start_time:
            return obj.start_time.date()
        return None

    @admin.display(description='Duration (minutes)')
    def get_duration(self, obj):
        if obj.start_time and obj.end_time:
            duration = obj.end_time - obj.start_time
            return round(duration.total_seconds() / 60)
        return None

admin.site.register(Hike, HikeAdmin)
