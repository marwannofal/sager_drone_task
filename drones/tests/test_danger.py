from django.test import TestCase
from drones.services.danger import DangerClassifier, DroneState, HeightRule, SpeedRule

class DangerTests(TestCase):
    def test_height_rule(self):
        c = DangerClassifier([HeightRule(500)])
        reasons = c.classify(DroneState(height=501, horizontal_speed=0))
        self.assertIn("height > 500m", reasons)

    def test_speed_rule(self):
        c = DangerClassifier([SpeedRule(10)])
        reasons = c.classify(DroneState(height=0, horizontal_speed=10.1))
        self.assertIn("speed > 10m/s", reasons)
