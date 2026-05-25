from __future__ import annotations

from config import LIMITS
from diagnostics import Diagnostic, Severity
from process_snapshot import ProcessSnapshot
from recipe import StateSetpoints
from states import BrewState


class ProcessMonitor:
    """Prozessüberwachung für ERROR-Entscheidungen.

    - Soll-/Ist-Abweichung => ERROR
    - Sensor-/Datenplausibilität => ERROR
    - echte Gefährdung bleibt Aufgabe des SafetySystem => EMERGENCY
    """

    def evaluate(self, state: BrewState, snapshot: ProcessSnapshot, setpoints: StateSetpoints) -> list[Diagnostic]:
        findings: list[Diagnostic] = []


        if not snapshot.sensor_ok:
            findings.append(Diagnostic(Severity.ERROR, "SENSOR_BAD", "Mindestens ein Sensorsignal ist ungültig."))

        if snapshot.k2_fuellstand <= 0 and snapshot.k2_fuellstand_voll:
            findings.append(
                Diagnostic(
                    Severity.ERROR,
                    "LEVEL_IMPLAUSIBLE",
                    "K2 Vollsignal aktiv aber Füllstand = 0."
                )
            )

        if state is BrewState.MASHING:
            findings += self._check_temperature_window(
                "Maischetemperatur K2",
                snapshot.mash_temperature,
                snapshot.k2_temp_lower or setpoints.temperature_min_c,
                snapshot.k2_temp_upper or setpoints.temperature_max_c,
            )
        elif state is BrewState.BOILING:
            findings += self._check_temperature_window(
                "Kochtemperatur K2",
                snapshot.mash_temperature,
                snapshot.k2_temp_lower or setpoints.temperature_min_c,
                snapshot.k2_temp_upper or setpoints.temperature_max_c,
            )
        elif state is BrewState.COOLING:
            if setpoints.cooling_target_c is not None and snapshot.fermenting_temperature > setpoints.cooling_target_c + LIMITS.process_temperature_tolerance_c:
                findings.append(
                    Diagnostic(
                        Severity.WARNING,
                        "COOLING_NOT_REACHED",
                        f"Kühlziel noch nicht erreicht: {snapshot.fermenting_temperature:.2f} °C > {setpoints.cooling_target_c:.2f} °C.",
                    )
                )
        elif state is BrewState.FERMENTING:
            findings += self._check_temperature_window(
                "Gärtemperatur K4/Mobilsensor",
                snapshot.fermenting_temperature,
                setpoints.temperature_min_c,
                setpoints.temperature_max_c,
            )

        return findings


    def process_ok(self, state: BrewState, snapshot: ProcessSnapshot, setpoints: StateSetpoints) -> bool:
        return not any(d.severity is Severity.ERROR for d in self.evaluate(state, snapshot, setpoints))

    @staticmethod
    def _check_temperature_window(name: str, actual: float, lower: float | None, upper: float | None) -> list[Diagnostic]:
        if lower is None or upper is None:
            return []
        if actual < lower - LIMITS.process_temperature_tolerance_c:
            return [Diagnostic(Severity.ERROR, "TEMP_TOO_LOW", f"{name}: {actual:.2f} °C < {lower:.2f} °C.")]
        if actual > upper + LIMITS.process_temperature_tolerance_c:
            return [Diagnostic(Severity.ERROR, "TEMP_TOO_HIGH", f"{name}: {actual:.2f} °C > {upper:.2f} °C.")]
        return []