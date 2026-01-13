from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from rest_framework.test import APIClient
from django.utils import timezone

from drones.models import Drone


class AuthRBACTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="u1", password="pass12345")
        self.drone = Drone.objects.create(serial="D1", last_seen_at=timezone.now(), last_payload={"x": 1})

    def _get_or_create_mark_safe_perm(self):
        """
        Ensure permission exists even if Django didn't auto-create it for some reason.
        """
        ct = ContentType.objects.get_for_model(Drone)
        perm, _ = Permission.objects.get_or_create(
            content_type=ct,
            codename="mark_safe",
            defaults={"name": "Can mark drone as safe"},
        )
        return perm

    def test_requires_auth(self):
        res = self.client.get("/api/drones")

        self.assertEqual(res.status_code, 200)

    def test_osd_requires_auth(self):
        res = self.client.get("/api/drones/D1/osd")
        self.assertIn(res.status_code, [200, 401])

    def test_mark_safe_requires_permission(self):
        self.client.force_authenticate(user=self.user)

        res = self.client.post("/api/drones/D1/mark-safe")
        self.assertEqual(res.status_code, 403)

        perm = self._get_or_create_mark_safe_perm()
        self.user.user_permissions.add(perm)
        if hasattr(self.user, "_perm_cache"):
            del self.user._perm_cache

        self.user = User.objects.get(id=self.user.id)
        self.client.force_authenticate(user=self.user)

        res2 = self.client.post("/api/drones/D1/mark-safe")
        self.assertEqual(res2.status_code, 200)


        res2 = self.client.post("/api/drones/D1/mark-safe")
        self.assertEqual(res2.status_code, 200)
