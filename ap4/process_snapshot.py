from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Any, Mapping


def _float(values: Mapping[str, Any], name: str, default: float = 0.0) -> float:
    value = values.get(name, default)
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bool(values: Mapping[str, Any], name: str, default: bool = False) -> bool:
    value = values.get(name, default)
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"true", "1", "ja", "yes", "on"}:
        return True
    if text in {"false", "0", "nein", "no", "off"}:
        return False
    return default


def _int(values: Mapping[str, Any], name: str, default: int = 0) -> int:
    value = values.get(name, default)
    if value in (None, ""):
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _str(values: Mapping[str, Any], name: str, default: str = "") -> str:
    value = values.get(name, default)
    if value is None:
        return default
    return str(value)


def _timestamp_to_seconds(timestamp: str) -> float:
    if not timestamp:
        return 0.0
    try:
        text = timestamp.replace("Z", "+00:00")
        return datetime.fromisoformat(text).timestamp()
    except ValueError:
        return 0.0


@dataclass(frozen=True)
class ProcessSnapshot:
    """Normiertes AP4-Prozessabbild pro Timestamp.

    Diese Klasse ist die Laufzeitschnittstelle AP3 -> AP4. AP3 liefert CSV,
    SQLite, MQTT oder Live-Werte. AP4 normiert sie auf genau diese Signale.
    Der Snapshot folgt dem vom Benutzer vorgegebenen Format: Es gibt nur einen
    gemessenen Durchfluss, nämlich K1 -> K2.
    """

    timestamp: str = ""
    timestamp_s: float = 0.0
    aktueller_schritt: int = 0
    start_requested: bool = False
    acknowledge: bool = False
    reset_requested: bool = False
    emergency_stop: bool = False
    sensor_ok: bool = True
    data_quality: str = "GOOD"

    # K1 = Nachgussbehälter
    k1_temperature_c: float = 78.0
    k1_level_l: float = 20.0

    # K2 = Maische-/Kochbehälter
    k2_temperature_c: float = 20.0
    k2_level_l: float = 0.0

    # K3 = Läuterbehälter
    k3_temperature_c: float = 20.0
    k3_level_l: float = 0.0

    # K4 = Gärbehälter
    k4_temperature_c: float = 20.0
    k4_level_l: float = 0.0

    # Einziger gemessener Durchfluss: K1 -> K2
    durchfluss_k1_k2_l_min: float = 0.0

    v3_open: bool = False
    v4_open: bool = False
    v5_open: bool = False
    pump_on: bool = False

    missing_value_age_s: float = 0.0

    @classmethod
    def from_dict(cls, values: Mapping[str, Any]) -> "ProcessSnapshot":
        """Erzeugt einen Snapshot aus CSV-/SQLite-/AP3-Daten.

        Unterstützt deutsche AP3-Feldnamen wie `k1_temperatur` und interne
        Feldnamen wie `k1_temperature_c`. Dadurch bleibt AP4 robust gegenüber
        unterschiedlichen AP3-Exportformaten.
        """
        aliases = dict(values)
        # Deutsche AP3-Signale -> kanonische AP4-Felder
        mapping = {
            "k1_temperatur": "k1_temperature_c",
            "k1_fuellstand": "k1_level_l",
            "k2_temperatur": "k2_temperature_c",
            "k2_fuellstand": "k2_level_l",
            "k3_temperatur": "k3_temperature_c",
            "k3_fuellstand": "k3_level_l",
            "k4_temperatur": "k4_temperature_c",
            "k4_fuellstand": "k4_level_l",
            "durchfluss_k1_k2": "durchfluss_k1_k2_l_min",
            "durchfluss_nachguss_maische": "durchfluss_k1_k2_l_min",
            "pump_on_feedback": "pump_on",
        }
        for src, dst in mapping.items():
            if src in aliases and dst not in aliases:
                aliases[dst] = aliases[src]

        timestamp = _str(aliases, "timestamp")
        timestamp_s = _float(aliases, "timestamp_s", _timestamp_to_seconds(timestamp))

        # Wenn AP3 nur aktueller_schritt liefert, kann AP4 damit den Start ableiten.
        start_requested = _bool(aliases, "start_requested", _int(aliases, "aktueller_schritt") > 0)

        return cls(
            timestamp=timestamp,
            timestamp_s=timestamp_s,
            aktueller_schritt=_int(aliases, "aktueller_schritt"),
            start_requested=start_requested,
            acknowledge=_bool(aliases, "acknowledge"),
            reset_requested=_bool(aliases, "reset_requested"),
            emergency_stop=_bool(aliases, "emergency_stop"),
            sensor_ok=_bool(aliases, "sensor_ok", True),
            data_quality=_str(aliases, "data_quality", "GOOD").upper(),
            k1_temperature_c=_float(aliases, "k1_temperature_c", 78.0),
            k1_level_l=_float(aliases, "k1_level_l", 20.0),
            k2_temperature_c=_float(aliases, "k2_temperature_c", 20.0),
            k2_level_l=_float(aliases, "k2_level_l", 0.0),
            k3_temperature_c=_float(aliases, "k3_temperature_c", 20.0),
            k3_level_l=_float(aliases, "k3_level_l", 0.0),
            k4_temperature_c=_float(aliases, "k4_temperature_c", 20.0),
            k4_level_l=_float(aliases, "k4_level_l", 0.0),
            durchfluss_k1_k2_l_min=_float(aliases, "durchfluss_k1_k2_l_min"),
            v3_open=_bool(aliases, "v3_open"),
            v4_open=_bool(aliases, "v4_open"),
            v5_open=_bool(aliases, "v5_open"),
            pump_on=_bool(aliases, "pump_on"),
            missing_value_age_s=_float(aliases, "missing_value_age_s"),
        )

    def with_updates(self, **changes: Any) -> "ProcessSnapshot":
        return replace(self, **changes)

    def to_ap3_like_dict(self) -> dict[str, Any]:
        """Exportiert die Werte in der Form, die im Bild vorgegeben wurde."""
        return {
            "timestamp": self.timestamp,
            "aktueller_schritt": self.aktueller_schritt,
            "k1_temperatur": self.k1_temperature_c,
            "k1_fuellstand": self.k1_level_l,
            "k2_temperatur": self.k2_temperature_c,
            "k2_fuellstand": self.k2_level_l,
            "k3_temperatur": self.k3_temperature_c,
            "k3_fuellstand": self.k3_level_l,
            "k4_temperatur": self.k4_temperature_c,
            "k4_fuellstand": self.k4_level_l,
            "durchfluss_k1_k2": self.durchfluss_k1_k2_l_min,
            "v3_open": self.v3_open,
            "v4_open": self.v4_open,
            "v5_open": self.v5_open,
            "pump_on": self.pump_on,
            "emergency_stop": self.emergency_stop,
            "sensor_ok": self.sensor_ok,
            "data_quality": self.data_quality,
            "start_requested": self.start_requested,
            "acknowledge": self.acknowledge,
        }
