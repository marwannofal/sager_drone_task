from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from drones.models import Drone, DroneTelemetryPoint

class ApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_filter_serial(self):
        Drone.objects.create(serial="ABC123")
        Drone.objects.create(serial="XYZ999")
        res = self.client.get("/api/drones?serial=abc")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 1)
        self.assertEqual(res.json()[0]["serial"], "ABC123")

    def test_path_geojson(self):
        d = Drone.objects.create(serial="DRONE1", latitude=1, longitude=2, last_seen_at=timezone.now())
        DroneTelemetryPoint.objects.create(drone=d, timestamp=timezone.now(), latitude=1, longitude=2)
        DroneTelemetryPoint.objects.create(drone=d, timestamp=timezone.now(), latitude=2, longitude=3)

        res = self.client.get("/api/drones/DRONE1/path")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(body["geometry"]["type"], "LineString")
        self.assertEqual(len(body["geometry"]["coordinates"]), 2)

    def test_nearby_validation(self):
        res = self.client.get("/api/drones/nearby?lat=999&lon=0")
        self.assertEqual(res.status_code, 400)
