from django.contrib import admin
from django_admin_inline_paginator.admin import TabularInlinePaginated
from django.db.models import Min, Max
import json

from .models import Hike, TrackPoint, HeartRateZone


class HeartRateZoneAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'mhr', 'rhr', 'zone_1', 'zone_2', 'zone_3', 'zone_4', 'zone_5')
    fields = ('mhr', 'rhr')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # obj is not None, so this is an existing object
            return ['mhr', 'rhr']
        return []

admin.site.register(HeartRateZone, HeartRateZoneAdmin)


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
        return queryset.annotate(
            start_time=Min('points__datetime'),
            end_time=Max('points__datetime')
        )

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        hike = self.get_object(request, object_id)
        trackpoints = hike.points.order_by('datetime')

        if trackpoints:
            start_time = trackpoints.first().datetime

            # Find the most recent heart rate zone created before the hike's start time
            hr_zones = HeartRateZone.objects.filter(date_created__lte=start_time).order_by('-date_created').first()
            if hr_zones:
                extra_context['hr_zones'] = json.dumps({
                    'zone_1': hr_zones.zone_1,
                    'zone_2': hr_zones.zone_2,
                    'zone_3': hr_zones.zone_3,
                    'zone_4': hr_zones.zone_4,
                    'zone_5': hr_zones.zone_5,
                })

                # Calculate time in each zone
                time_in_zones_seconds = {
                    'Zone 1': 0, 'Zone 2': 0, 'Zone 3': 0,
                    'Zone 4': 0, 'Zone 5': 0, 'Below Zone 1': 0
                }
                total_duration_seconds = (trackpoints.last().datetime - trackpoints.first().datetime).total_seconds()

                for i in range(1, len(trackpoints)):
                    p1 = trackpoints[i-1]
                    p2 = trackpoints[i]
                    if p1.heart_rate is not None:
                        duration_seconds = (p2.datetime - p1.datetime).total_seconds()
                        hr = p1.heart_rate
                        if hr < hr_zones.zone_1:
                            time_in_zones_seconds['Below Zone 1'] += duration_seconds
                        elif hr < hr_zones.zone_2:
                            time_in_zones_seconds['Zone 1'] += duration_seconds
                        elif hr < hr_zones.zone_3:
                            time_in_zones_seconds['Zone 2'] += duration_seconds
                        elif hr < hr_zones.zone_4:
                            time_in_zones_seconds['Zone 3'] += duration_seconds
                        elif hr < hr_zones.zone_5:
                            time_in_zones_seconds['Zone 4'] += duration_seconds
                        else:
                            time_in_zones_seconds['Zone 5'] += duration_seconds

                # Format times and calculate percentages for display
                ordered_zones = ['Zone 5', 'Zone 4', 'Zone 3', 'Zone 2', 'Zone 1', 'Below Zone 1']
                time_in_zones_display = []
                spider_chart_data = {'labels': [], 'data': []}
                for zone in ordered_zones:
                    time_in_seconds = time_in_zones_seconds.get(zone, 0)
                    percentage = (time_in_seconds / total_duration_seconds * 100) if total_duration_seconds > 0 else 0
                    time_in_zones_display.append({
                        'zone': zone,
                        'time': f"{int(time_in_seconds // 60)}m {int(time_in_seconds % 60)}s",
                        'percentage': f"{percentage:.1f}%"
                    })
                    spider_chart_data['labels'].append(zone)
                    spider_chart_data['data'].append(percentage)
                extra_context['time_in_zones'] = time_in_zones_display
                extra_context['spider_chart_data'] = json.dumps(spider_chart_data)
            else:
                extra_context['hr_zones'] = json.dumps(None)
                extra_context['time_in_zones'] = None
                extra_context['spider_chart_data'] = json.dumps(None)

            time_diffs = [(tp.datetime - start_time).total_seconds() / 60 for tp in trackpoints]
            heart_rates = [tp.heart_rate for tp in trackpoints]

            # Simple Moving Average
            def moving_average(data, window_size):
                if not data or window_size <= 0:
                    return []
                # Calculate the moving average
                smoothed = []
                for i in range(len(data)):
                    start = max(0, i - window_size + 1)
                    window = [x for x in data[start:i+1] if x is not None]
                    if window:
                        smoothed.append(sum(window) / len(window))
                    else:
                        smoothed.append(None)
                return smoothed

            smoothed_heart_rates = moving_average(heart_rates, 5)  # Using a window of 5

            chart_points = []
            for i in range(len(time_diffs)):
                chart_points.append({
                    'x': time_diffs[i],
                    'y': smoothed_heart_rates[i]
                })

            extra_context['chart_data'] = json.dumps({
                'datasets': [{
                    'label': 'Smoothed Heart Rate',
                    'data': chart_points,
                    'borderColor': 'rgb(75, 192, 192)',
                    'tension': 0.1,
                    'yAxisID': 'y',
                }]
            })
        else:
            # No trackpoints, so no chart data
            extra_context['hr_zones'] = json.dumps(None)
            extra_context['chart_data'] = json.dumps(None)


        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    @admin.display(description='Date', ordering='start_time')
    def get_date(self, obj):
        if hasattr(obj, 'start_time') and obj.start_time:
            return obj.start_time.date()
        return None

    @admin.display(description='Duration (minutes)')
    def get_duration(self, obj):
        if hasattr(obj, 'start_time') and obj.start_time and hasattr(obj, 'end_time') and obj.end_time:
            duration = obj.end_time - obj.start_time
            return round(duration.total_seconds() / 60)
        return None

admin.site.register(Hike, HikeAdmin)
