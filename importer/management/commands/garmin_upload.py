import io
import os
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
import xml.etree.ElementTree as ET

from importer.models import Hike, TrackPoint

class Command(BaseCommand):
    help = 'Converts .gmn files to .xml like string format,' \
    'processes them, and uploads to the database.'

    def handle(self, *args, **options):
        save_runs_process = subprocess.run('garmin_save_runs', shell=True, check=True, text=True, capture_output=True)
        if str(save_runs_process.stdout).startswith('garmin unit could not be opened'):
            self.stdout.write(self.style.ERROR(save_runs_process.stdout))
        else:
            self.stdout.write(self.style.SUCCESS(save_runs_process.stdout))
        gmn_dir = os.path.join(settings.BASE_DIR, 'garmin_data')
        existing_hike_names = set(Hike.objects.all().values_list('file_name', flat=True))
        for dirpath, _, filenames in os.walk(gmn_dir):
            for filename in filenames:
                if filename.lower().endswith('.gmn'):
                    full_file_path = os.path.join(dirpath, filename)
                    process = subprocess.run(f'garmin_dump {full_file_path}', shell=True, check=True, text=True, capture_output=True)
                    content = f"<activities>\n{process.stdout}</activities>"
                    f = io.StringIO(content)
                    tree = ET.parse(f)
                    root = tree.getroot()
                    hike_element = root.find('run')
                    if hike_element is None:
                        self.stdout.write(self.style.WARNING(f"Hike element is null for {filename}"))
                        continue
                    point_element = root.findall('point')
                    if point_element is None:
                        self.stdout.write(self.style.WARNING(f"Point element is null for {filename}"))
                        continue
                    if filename in existing_hike_names:
                        self.stdout.write(self.style.NOTICE(f'Hike with file_name {filename} already exists. Skipping.'))
                        continue
                    trackpoints = set()
                    with transaction.atomic():
                        hike_instance = Hike.objects.create(
                            file_name=filename
                        )
                        for point in root.findall('point'):
                            time = point.get('time')
                            lat = point.get('lat')
                            lon = point.get('lon')
                            alt = point.get('alt')
                            heart_rate = point.get('hr')
                            trackpoint = TrackPoint(
                                hike=hike_instance,
                                datetime=time,
                                lat=float(lat)if lat else None,
                                lon=float(lon) if lon else None,
                                altitude=float(alt) if alt else None,
                                heart_rate=int(heart_rate) if heart_rate else None
                            )
                            trackpoints.add(trackpoint)
                    TrackPoint.objects.bulk_create(
                        trackpoints
                    )
                    self.stdout.write(self.style.SUCCESS(f'Processed file {filename} successfully'))
