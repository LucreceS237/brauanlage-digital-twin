from __future__ import annotations

from .config import EngineeringLimits, LIMITS
from .diagnostics import Diagnostic, Severity, make_diagnostic
from .fault_catalog import FaultCode
from .process_snapshot import ProcessSnapshot


class SafetySystem:
    """Safety-Prüfung hat höchste Priorität vor ERROR und Normalpfad."""

    def __init__(self, limits: EngineeringLimits = LIMITS) -> None:
        self.limits = limits

    def evaluate(self, snapshot: ProcessSnapshot) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        if snapshot.emergency_stop:
            diagnostics.append(make_diagnostic(Severity.EMERGENCY, FaultCode.EMERGENCY_001_ESTOP_ACTIVE, "emergency_stop", True, "False required"))
        if not snapshot.sensor_ok:
            diagnostics.append(make_diagnostic(Severity.EMERGENCY, FaultCode.EMERGENCY_002_SENSOR_NOT_OK, "sensor_ok", False, "True required"))
        if snapshot.missing_value_age_s > self.limits.max_missing_value_age_s:
            diagnostics.append(make_diagnostic(Severity.EMERGENCY, FaultCode.EMERGENCY_019_DATA_STALE, "missing_value_age_s", snapshot.missing_value_age_s, self.limits.max_missing_value_age_s))

        temp_map = (
            ("k1_temperature_c", snapshot.k1_temperature_c, FaultCode.EMERGENCY_003_K1_TEMP_TOO_LOW, FaultCode.EMERGENCY_004_K1_TEMP_TOO_HIGH),
            ("k2_temperature_c", snapshot.k2_temperature_c, FaultCode.EMERGENCY_005_K2_TEMP_TOO_LOW, FaultCode.EMERGENCY_006_K2_TEMP_TOO_HIGH),
            ("k3_temperature_c", snapshot.k3_temperature_c, FaultCode.EMERGENCY_007_K3_TEMP_TOO_LOW, FaultCode.EMERGENCY_008_K3_TEMP_TOO_HIGH),
            ("k4_temperature_c", snapshot.k4_temperature_c, FaultCode.EMERGENCY_009_K4_TEMP_TOO_LOW, FaultCode.EMERGENCY_010_K4_TEMP_TOO_HIGH),
        )
        for signal, value, low_code, high_code in temp_map:
            if value < self.limits.absolute_min_temperature_c:
                diagnostics.append(make_diagnostic(Severity.EMERGENCY, low_code, signal, value, self.limits.absolute_min_temperature_c))
            if value > self.limits.absolute_max_temperature_c:
                diagnostics.append(make_diagnostic(Severity.EMERGENCY, high_code, signal, value, self.limits.absolute_max_temperature_c))

        level_map = (
            ("k1_level_l", snapshot.k1_level_l, FaultCode.EMERGENCY_011_K1_LEVEL_NEGATIVE, FaultCode.EMERGENCY_012_K1_LEVEL_TOO_HIGH),
            ("k2_level_l", snapshot.k2_level_l, FaultCode.EMERGENCY_013_K2_LEVEL_NEGATIVE, FaultCode.EMERGENCY_014_K2_LEVEL_TOO_HIGH),
            ("k3_level_l", snapshot.k3_level_l, FaultCode.EMERGENCY_015_K3_LEVEL_NEGATIVE, FaultCode.EMERGENCY_016_K3_LEVEL_TOO_HIGH),
            ("k4_level_l", snapshot.k4_level_l, FaultCode.EMERGENCY_017_K4_LEVEL_NEGATIVE, FaultCode.EMERGENCY_018_K4_LEVEL_TOO_HIGH),
        )
        for signal, value, low_code, high_code in level_map:
            if value < self.limits.min_level_l:
                diagnostics.append(make_diagnostic(Severity.EMERGENCY, low_code, signal, value, self.limits.min_level_l))
            if value > self.limits.max_level_l:
                diagnostics.append(make_diagnostic(Severity.EMERGENCY, high_code, signal, value, self.limits.max_level_l))
        return diagnostics
