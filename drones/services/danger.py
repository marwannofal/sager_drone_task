from dataclasses import dataclass
from typing import List, Protocol, Optional

@dataclass(frozen=True)
class DroneState:
    height: Optional[float]
    horizontal_speed: Optional[float]

class DangerRule(Protocol):
    def check(self, state: DroneState) -> Optional[str]:
        ...

class HeightRule:
    def __init__(self, max_height_m: float):
        self.max_height_m = max_height_m

    def check(self, state: DroneState) -> Optional[str]:
        if state.height is None:
            return None
        if state.height > self.max_height_m:
            return f"height > {self.max_height_m}m"
        return None

class SpeedRule:
    def __init__(self, max_speed_ms: float):
        self.max_speed_ms = max_speed_ms

    def check(self, state: DroneState) -> Optional[str]:
        if state.horizontal_speed is None:
            return None
        if state.horizontal_speed > self.max_speed_ms:
            return f"speed > {self.max_speed_ms}m/s"
        return None

class DangerClassifier:
    """
    Classifies drone states based on danger rules.
    """
    def __init__(self, rules: List[DangerRule]):
        self.rules = rules

    def classify(self, state: DroneState) -> List[str]:
        reasons: List[str] = []
        for rule in self.rules:
            reason = rule.check(state)
            if reason:
                reasons.append(reason)
        return reasons