from django.db import models

class Run(models.Model):
    TYPE_CHOICES = [
        ('running', 'Running'),
        ('cycling', 'Cycling'),
        # Add other sports as needed
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    sport = models.CharField(max_length=20)
    multisport = models.BooleanField(default=False)
    file_name = models.CharField(max_length=255, unique=True)

class Lap(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name='laps')
    index = models.IntegerField()
    start_time = models.DateTimeField()
    duration = models.DurationField()
    distance = models.FloatField()
    trigger = models.CharField(max_length=20)
    begin_lat = models.FloatField()
    begin_lon = models.FloatField()
    end_lat = models.FloatField()
    end_lon = models.FloatField()
    max_speed = models.FloatField()
    calories = models.IntegerField()
    intensity = models.CharField(max_length=20)

class TrackPoint(models.Model):
    lap = models.ForeignKey(Lap, on_delete=models.CASCADE, related_name='track_points')
    time = models.DateTimeField()
    lat = models.FloatField()
    lon = models.FloatField()
    alt = models.FloatField(null=True, blank=True)
    distance = models.FloatField(null=True, blank=True)
    heart_rate = models.IntegerField(null=True, blank=True)
