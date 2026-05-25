from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


def _float(values: Mapping[str, Any], name: str, default: float = 0.0) -> float:
    value = values.get(name, default)
    if value is None:
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
    return str(value).strip().lower() in {"true", "1", "ja", "yes", "on"}


def _int(values: Mapping[str, Any], name: str, default: int = 0) -> int:
    value = values.get(name, default)
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class ProcessSnapshot:
    """Normiertes Prozessabbild aus den OPC-UA-Knoten.

    Fachliche Zuordnung aus der Excel-Datei:
    - K1 = Nachgussbehälter
    - K2 = Maischebehälter
    - K3 = Läuterbehälter
    - K4/Gärbereich = mobiler Temperatursensor

    Diese Klasse abstrahiert bewusst von den SPS-Namen. Der Zustandsautomat
    arbeitet mit fachlichen Signalen, nicht mit NodeIds.
    """

    aktueller_schritt: int
    durchfluss_nachguss_maische: float

    k1_temperatur: float
    k1_fuellstand_voll: bool
    k1_temp_upper: float | None
    k1_temp_lower: float | None

    k2_temperatur: float
    k2_fuellstand: float
    k2_fuellstand_voll: bool
    k2_temp_upper: float | None
    k2_temp_lower: float | None

    k3_temperatur: float
    k3_fuellstand: float
    k3_temp_upper: float | None
    k3_temp_lower: float | None
    k3_level_max: float | None
    k3_level_min: float | None

    mobiler_sensor_temperatur: float

    start_requested: bool = False
    acknowledge: bool = False
    emergency_stop: bool = False
    sensor_ok: bool = True

    @property
    def mash_temperature(self) -> float:
        return self.k2_temperatur

    @property
    def mash_level(self) -> float:
        return self.k2_fuellstand

    @property
    def lautering_temperature(self) -> float:
        return self.k3_temperatur

    @property
    def lautering_level(self) -> float:
        return self.k3_fuellstand

    @property
    def fermenting_temperature(self) -> float:
        return self.mobiler_sensor_temperatur

    @classmethod
    def from_opc_values(
        cls,
        values: Mapping[str, Any],
        *,
        start_requested: bool = False,
        acknowledge: bool = False,
        emergency_stop: bool = False,
    ) -> "ProcessSnapshot":
        zero_to_none = lambda x: None if x == 0 else x
        k1_upper = zero_to_none(_float(values, "k1_temperatur_sollwert_obere_grenze", 0.0))
        k1_lower = zero_to_none(_float(values, "k1_temperatur_sollwert_untere_grenze", 0.0))
        k2_upper = zero_to_none(_float(values, "k2_temperatur_sollwert_obere_grenze", 0.0))
        k2_lower = zero_to_none(_float(values, "k2_temperatur_sollwert_untere_grenze", 0.0))
        k3_upper = zero_to_none(_float(values, "k3_temperatur_sollwert_obere_grenze", 0.0))
        k3_lower = zero_to_none(_float(values, "k3_temperatur_sollwert_untere_grenze", 0.0))

        return cls(
            aktueller_schritt=_int(values, "aktueller_schritt", 0),
            durchfluss_nachguss_maische=_float(values, "durchfluss_nachguss_maische", 0.0),
            k1_temperatur=_float(values, "k1_temperatur", 20.0),
            k1_fuellstand_voll=_bool(values, "k1_fuellstand_voll", False),
            k1_temp_upper=k1_upper,
            k1_temp_lower=k1_lower,
            k2_temperatur=_float(values, "k2_temperatur", 20.0),
            k2_fuellstand=_float(values, "k2_fuellstand", 0.0),
            k2_fuellstand_voll=_bool(values, "k2_fuellstand_voll", False),
            k2_temp_upper=k2_upper,
            k2_temp_lower=k2_lower,
            k3_temperatur=_float(values, "k3_temperatur", 20.0),
            k3_fuellstand=_float(values, "k3_fuellstand", 0.0),
            k3_temp_upper=k3_upper,
            k3_temp_lower=k3_lower,
            k3_level_max=zero_to_none(_float(values, "k3_maximaler_fuellstand", 0.0)),
            k3_level_min=zero_to_none(_float(values, "k3_minimaler_fuellstand", 0.0)),
            mobiler_sensor_temperatur=_float(values, "mobiler_sensor_temperatur", 20.0),
            start_requested=start_requested,
            acknowledge=acknowledge,
            emergency_stop=emergency_stop,
            sensor_ok=True,
        )