from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType

from drones.models import Drone, NoFlyZone


class Command(BaseCommand):
    help = "Bootstrap demo users/groups/permissions for local/docker demo."

    def handle(self, *args, **options):
        # Ensure custom permissions exist
        drone_ct = ContentType.objects.get_for_model(Drone)
        zone_ct = ContentType.objects.get_for_model(NoFlyZone)

        mark_safe, _ = Permission.objects.get_or_create(
            content_type=drone_ct,
            codename="mark_safe",
            defaults={"name": "Can mark drone as safe"},
        )
        modify_settings, _ = Permission.objects.get_or_create(
            content_type=zone_ct,
            codename="modify_settings",
            defaults={"name": "Can modify settings"},
        )

        operators, _ = Group.objects.get_or_create(name="operators")
        admins, _ = Group.objects.get_or_create(name="admins")

        operators.permissions.add(mark_safe)
        admins.permissions.add(mark_safe, modify_settings)

        # Users
        admin1, _ = User.objects.get_or_create(username="admin1", defaults={"is_staff": True, "is_superuser": False})
        admin1.set_password("Aa@123456")
        admin1.save()
        admin1.groups.add(admins)

        operator1, _ = User.objects.get_or_create(username="operator1")
        operator1.set_password("Aa@123456")
        operator1.save()
        operator1.groups.add(operators)

        self.stdout.write(self.style.SUCCESS("Bootstrap done: users admin1/operator1 (pass Aa@123456), groups + perms set."))
