"""
File: test_alarm_adapter.py
Work Package: tests
Responsible Engineer: Engineer D
Purpose: Verify AP4 diagnostics convert into AP5 alarms with correct severity and approved-vessel component labels.
"""
from project.ap4.diagnostics import Severity, make_diagnostic
from project.ap4.fault_catalog import FaultCode
from project.ap5.adapters.ap4_alarm_adapter import diagnostic_to_alarm


def test_severity_mapping_and_component_label():
    # AP4 k1_temperature_c is, after correction, the K2 Maischebehälter.
    diag = make_diagnostic(
        Severity.ERROR, FaultCode.ERROR_005_K1_MASHING_TEMP_LOW,
        signal="k1_temperature_c", value=40.0, limit=62.0,
    )
    alarm = diagnostic_to_alarm(diag, display_state="ERROR_005_K1_MASHING_TEMP_LOW")
    assert alarm.severity == "HIGH"
    assert alarm.component == "K2 Maischebehälter"
    assert alarm.code == "ERROR_005_K1_MASHING_TEMP_LOW"
    assert alarm.variable == "k1_temperature_c"
    assert alarm.threshold == "62.0"


def test_emergency_maps_to_critical():
    diag = make_diagnostic(
        Severity.EMERGENCY, FaultCode.EMERGENCY_001_ESTOP_ACTIVE,
        signal="emergency_stop", value=True, limit="False required",
    )
    alarm = diagnostic_to_alarm(diag, display_state="EMERGENCY_001_ESTOP_ACTIVE")
    assert alarm.severity == "CRITICAL"
