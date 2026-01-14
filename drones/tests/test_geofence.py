from django.test import TestCase
from drones.models import NoFlyZone
from drones.services.geofence import check_geofence


class GeofenceTests(TestCase):
    def test_polygon_zone_inside(self):
        NoFlyZone.objects.create(
            name="Poly",
            shape="polygon",
            polygon=[
                [35.80, 31.97],
                [35.85, 31.97],
                [35.85, 32.00],
                [35.80, 32.00],
            ],
            is_active=True,
        )

        reason = check_geofence(31.98, 35.82)  # lat, lon inside polygon
        self.assertEqual(reason, "entered_no_fly_zone")

    def test_polygon_zone_outside(self):
        NoFlyZone.objects.create(
            name="Poly",
            shape="polygon",
            polygon=[
                [35.80, 31.97],
                [35.85, 31.97],
                [35.85, 32.00],
                [35.80, 32.00],
            ],
            is_active=True,
        )

        reason = check_geofence(31.50, 35.82)  # far away
        self.assertIsNone(reason)
