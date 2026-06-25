# guards.py
from config import (
    START_TEMP,
    MIN_TEMP,
    MAX_TEMP,
    MIN_K1_LEVEL,
    MIN_FLOW_RATE,
    MAX_LEVEL,
)
from recipe import StateSetpoints
from snapshot import ProcessSnapshot


def emergency(snapshot: ProcessSnapshot) -> bool:
    return snapshot.emergency_stop


def can_leave_emergency(snapshot: ProcessSnapshot) -> bool:
    return not snapshot.emergency_stop and snapshot.acknowledge


def _level_fault(level: float) -> bool:
    return level < 0 or level > MAX_LEVEL


def _temp_fault(temperature: float) -> bool:
    return temperature < MIN_TEMP or temperature > MAX_TEMP


def process_fault(snapshot: ProcessSnapshot) -> bool:
    if not snapshot.sensor_ok:
        return True
    for temp in (snapshot.k1_temperature, snapshot.k2_temperature, snapshot.k3_temperature):
        if _temp_fault(temp):
            return True
    for level in (snapshot.k1_level, snapshot.k2_level, snapshot.k3_level):
        if _level_fault(level):
            return True
    return False


def can_leave_error(snapshot: ProcessSnapshot) -> bool:
    return not process_fault(snapshot) and snapshot.acknowledge


def can_start_brewing(snapshot: ProcessSnapshot, mashing: StateSetpoints) -> bool:
    return (
        snapshot.start_requested
        and snapshot.k1_temperature > START_TEMP
        and snapshot.k1_level >= MIN_K1_LEVEL
    )

# Guard bewusst zeitbasiert – Temperatur wird vom Regler stabilisiert
def mash_finished(time_in_state: float, setpoints: StateSetpoints) -> bool:
    if setpoints.duration_s is None:
        return False
    return time_in_state >= setpoints.duration_s


def lautering_finished(
    time_in_state: float, snapshot: ProcessSnapshot, setpoints: StateSetpoints
) -> bool:
    if setpoints.duration_s is None:
        return False
    return (
        time_in_state >= setpoints.duration_s
        and snapshot.flow_rate >= MIN_FLOW_RATE
    )


def boiling_finished(time_in_state: float, setpoints: StateSetpoints) -> bool:
    if setpoints.duration_s is None:
        return False
    return time_in_state >= setpoints.duration_s


def cooled_down(snapshot: ProcessSnapshot, setpoints: StateSetpoints) -> bool:
    if setpoints.cooling_target is None:
        return False
    return snapshot.k3_temperature <= setpoints.cooling_target


def fermentation_finished(time_in_state: float, setpoints: StateSetpoints) -> bool:
    if setpoints.duration_s is None:
        return False
    return time_in_state >= setpoints.duration_s
