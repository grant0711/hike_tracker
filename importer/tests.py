import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Hike, TrackPoint, HeartRateZone


class HeartRateZoneTest(TestCase):
    def test_zone_calculation(self):
        """
        Tests that the heart rate zones are calculated correctly based on the
        Karvonen formula.
        """
        # Example values from a known calculator
        # https://www.omnicalculator.com/sports/target-heart-rate
        hr_zones = HeartRateZone.objects.create(mhr=180, rhr=60)
        self.assertEqual(hr_zones.zone_1, 120)
        self.assertEqual(hr_zones.zone_2, 132)
        self.assertEqual(hr_zones.zone_3, 144)
        self.assertEqual(hr_zones.zone_4, 156)
        self.assertEqual(hr_zones.zone_5, 168)

User = get_user_model()


class HikeAdminTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            "admin", "admin@example.com", "password"
        )
        self.client.login(username="admin", password="password")
        self.hike = Hike.objects.create(name="Test Hike")
        # Create trackpoints, some with heart_rate=None
        now = datetime.datetime.now(datetime.timezone.utc)
        TrackPoint.objects.create(
            hike=self.hike,
            datetime=now,
            lat=40.7128,
            lon=-74.0060,
            heart_rate=120,
        )
        TrackPoint.objects.create(
            hike=self.hike,
            datetime=now + datetime.timedelta(minutes=1),
            lat=40.7129,
            lon=-74.0061,
            heart_rate=None,
        )
        TrackPoint.objects.create(
            hike=self.hike,
            datetime=now + datetime.timedelta(minutes=2),
            lat=40.7130,
            lon=-74.0062,
            heart_rate=125,
        )

    def test_hike_change_view_handles_none_heart_rate(self):
        """
        Tests that the Hike change view can be accessed without error
        when a TrackPoint has a null heart_rate.
        """
        url = reverse(
            "admin:importer_hike_change", args=[self.hike.pk]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_hike_list_view(self):
        """
        Tests that the Hike list view can be accessed without error.
        """
        url = reverse("admin:importer_hike_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)