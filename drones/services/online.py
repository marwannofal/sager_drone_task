from datetime import timedelta
from django.utils import timezone

def is_online(last_seen_at, window_seconds: int) -> bool:
    """
    Determine if a drone is online based on its last seen timestamp.

    Args:
        last_seen_at (datetime): The timestamp when the drone was last seen.
        window_seconds (int): The time window in seconds to consider a drone as online.

    Returns:
        bool: True if the drone is online, False otherwise.
    """
    if not last_seen_at:
        return False
    return timezone.now() - last_seen_at <= timedelta(seconds=window_seconds)