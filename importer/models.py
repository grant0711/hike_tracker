import uuid

from django.db import models

def create_uuid():
    return uuid.uuid4()

class Hike(models.Model):
    id = models.UUIDField(primary_key=True, default=create_uuid)
    file_name = models.CharField(max_length=255, unique=True, db_index=True)

class TrackPoint(models.Model):
    id = models.UUIDField(primary_key=True, default=create_uuid)
    hike = models.ForeignKey(Hike, on_delete=models.CASCADE, related_name='points')
    datetime = models.DateTimeField()
    lat = models.FloatField()
    lon = models.FloatField()
    alt = models.FloatField(null=True, blank=True)
    distance = models.FloatField(null=True, blank=True)
    heart_rate = models.IntegerField(null=True, blank=True)
