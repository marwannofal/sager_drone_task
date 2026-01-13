from django.test import TestCase
from drones.services.geo import haversine_km

class GeoTests(TestCase):
    def test_haversine_zero(self):
        self.assertAlmostEqual(haversine_km(0, 0, 0, 0), 0.0, places=6)
