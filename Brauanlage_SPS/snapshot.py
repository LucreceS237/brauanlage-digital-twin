# snapshot.py
from dataclasses import dataclass


@dataclass
class ProcessSnapshot:
    """Aktuelle Prozesswerte – Abbild der SPS-/Anlagenmessungen pro Zyklus."""

    # Bedienung / Sicherheit
    emergency_stop: bool
    start_requested: bool
    acknowledge: bool = False
    sensor_ok: bool = True

    # K1 – Maisch-/Kochkessel
    k1_temperature: float = 20.0   # °C Ist
    k1_level: float = 0.0          # % Füllstand

    # K2 – Lauter-/Zwischenbehälter
    k2_temperature: float = 20.0
    k2_level: float = 0.0

    # K3 – Gärbehälter
    k3_temperature: float = 20.0
    k3_level: float = 0.0

    setpoint_temperature: float = 65.0  # °C Soll (vom Regler aus fsm.temperature_setpoint)
    flow_rate: float = 0.0              # Durchfluss Nachguss / Lauter
    pump_on: bool = False               # Pumpen-Rückmeldung
    valve_open: bool = False            # Ventil-Rückmeldung
