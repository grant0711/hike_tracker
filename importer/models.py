import uuid

from django.db import models

def create_uuid():
    return uuid.uuid4()

class HikeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Hike(models.Model):

    objects = HikeManager()

    id = models.UUIDField(primary_key=True, default=create_uuid)
    file_name = models.CharField(max_length=255, unique=True, db_index=True)
    is_deleted = models.BooleanField(default=False)
    name = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

class TrackPoint(models.Model):
    id = models.UUIDField(primary_key=True, default=create_uuid)
    hike = models.ForeignKey(Hike, on_delete=models.CASCADE, related_name='points')
    datetime = models.DateTimeField()
    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)
    heart_rate = models.IntegerField(null=True)

    indexes = [
        models.Index(fields=['hike', 'datetime'], name='hike_datetime_idx'),
    ]
    unique_together = (('hike', 'datetime'),)
