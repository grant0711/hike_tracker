import uuid

from django.db import models

def create_uuid():
    return uuid.uuid4()

class HikeQuerySet(models.QuerySet):
    def delete(self):
        self.update(is_deleted=True)

class HikeManager(models.Manager):
    def get_queryset(self):
        return HikeQuerySet(self.model, using=self._db).filter(is_deleted=False)

class Hike(models.Model):

    objects = HikeManager.from_queryset(HikeQuerySet)()

    id = models.UUIDField(primary_key=True, default=create_uuid)
    file_name = models.CharField(max_length=255, unique=True, db_index=True)
    is_deleted = models.BooleanField(default=False)
    name = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

class TrackPoint(models.Model):
    id = models.UUIDField(primary_key=True, default=create_uuid)
    hike = models.ForeignKey(Hike, on_delete=models.CASCADE, related_name='points')
    datetime = models.DateTimeField()
    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)
    altitude = models.FloatField(null=True)
    heart_rate = models.IntegerField(null=True)

    indexes = [
        models.Index(fields=['hike', 'datetime'], name='hike_datetime_idx'),
    ]
    unique_together = (('hike', 'datetime'),)


class HeartRateZone(models.Model):
    id = models.UUIDField(primary_key=True, default=create_uuid)
    mhr = models.IntegerField(verbose_name="Maximum Heart Rate")
    rhr = models.IntegerField(verbose_name="Resting Heart Rate")
    zone_1 = models.IntegerField(editable=False)
    zone_2 = models.IntegerField(editable=False)
    zone_3 = models.IntegerField(editable=False)
    zone_4 = models.IntegerField(editable=False)
    zone_5 = models.IntegerField(editable=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"HR Zones (MHR: {self.mhr}, RHR: {self.rhr})"

    def save(self, *args, **kwargs):
        for i in range(1, 6):
            intensity = (50 + (i - 1) * 10) / 100
            zone_value = ((self.mhr - self.rhr) * intensity) + self.rhr
            setattr(self, f'zone_{i}', round(zone_value))
        super().save(*args, **kwargs)
