from __future__ import annotations

from config import LIMITS
from diagnostics import Diagnostic, Severity
from process_snapshot import ProcessSnapshot


class SafetySystem:
    """Sicherheitsbewertung.

    EMERGENCY wird nur für echte Gefährdungen gesetzt. Ein normaler
    Soll-Ist-Fehler ist ERROR und wird im ProcessMonitor behandelt.
    """

    def evaluate(self, snapshot: ProcessSnapshot) -> list[Diagnostic]:
        findings: list[Diagnostic] = []

        if snapshot.emergency_stop:
            findings.append(Diagnostic(Severity.EMERGENCY, "E_STOP", "Not-Aus ist aktiv."))

        for name, value in {
            "K1_Temperatur": snapshot.k1_temperatur,
            "K2_Temperatur": snapshot.k2_temperatur,
            "K3_Temperatur": snapshot.k3_temperatur,
            "MobilerSensor_Temperatur": snapshot.mobiler_sensor_temperatur,
        }.items():
            if value < LIMITS.absolute_min_temperature_c or value > LIMITS.absolute_max_temperature_c:
                findings.append(
                    Diagnostic(
                        Severity.EMERGENCY,
                        "ABS_TEMP_LIMIT",
                        f"{name}={value:.2f} °C verletzt absolute Sicherheitsgrenze.",
                    )
                )

        # K3-Füllstand war in der Tabelle orange/zu prüfen. Er wird trotzdem
        # verwendet, aber konservativ und mit klarer Diagnose.
        if snapshot.k3_level_max is not None and snapshot.k3_fuellstand > snapshot.k3_level_max:
            findings.append(
                Diagnostic(
                    Severity.EMERGENCY,
                    "K3_LEVEL_HIGH",
                    f"K3-Füllstand {snapshot.k3_fuellstand:.2f} L > Max {snapshot.k3_level_max:.2f} L.",
                )
            )
        if snapshot.k3_level_min is not None and snapshot.k3_fuellstand < snapshot.k3_level_min:
            findings.append(
                Diagnostic(
                    Severity.WARNING,
                    "K3_LEVEL_LOW",
                    f"K3-Füllstand {snapshot.k3_fuellstand:.2f} L < Min {snapshot.k3_level_min:.2f} L.",
                )
            )

        return findings

    def is_emergency(self, snapshot: ProcessSnapshot) -> bool:
        return any(d.severity is Severity.EMERGENCY for d in self.evaluate(snapshot))