from rest_framework.permissions import BasePermission
from drones.models import Drone

class CanMarkDroneSafe(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        app_label = Drone._meta.app_label
        return request.user.has_perm(f"{app_label}.mark_safe")


class CanModifySettings(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        app_label = Drone._meta.app_label
        return request.user.has_perm(f"{app_label}.modify_settings")
