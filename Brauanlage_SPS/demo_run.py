from __future__ import annotations

import logging
from pathlib import Path

from excel_node_repository import ExcelNodeRepository
from fsm import BrewStateMachine
from opcua_client import OpcUaCollector, SimulatedNodeReader
from process_snapshot import ProcessSnapshot
from states import BrewState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("brauanlage.demo")


def make_values(**overrides):
    # Werte basieren auf den API-Namen aus Top_Pflichtknoten / Projektrelevante_Knoten.
    values = {
        "aktueller_schritt": 0,
        "durchfluss_nachguss_maische": 1.0,
        "k1_fuellstand_voll": False,
        "k1_temperatur": 22.0,
        "k1_temperatur_sollwert_obere_grenze": 0.0,
        "k1_temperatur_sollwert_untere_grenze": 0.0,
        "k2_fuellstand": 10.0,
        "k2_fuellstand_voll": True,
        "k2_temperatur": 65.0,
        "k2_temperatur_sollwert_obere_grenze": 0.0,
        "k2_temperatur_sollwert_untere_grenze": 0.0,
        "k3_fuellstand": 20.0,
        "k3_temperatur": 70.0,
        "k3_temperatur_sollwert_obere_grenze": 0.0,
        "k3_temperatur_sollwert_untere_grenze": 0.0,
        "k3_maximaler_fuellstand": 50.0,
        "k3_minimaler_fuellstand": 6.0,
        "mobiler_sensor_temperatur": 20.0,
    }
    values.update(overrides)
    return values


def run_step(fsm: BrewStateMachine, values: dict, dt_s: float, *, start=False, ack=False, e_stop=False):
    snap = ProcessSnapshot.from_opc_values(values, start_requested=start, acknowledge=ack, emergency_stop=e_stop)
    result = fsm.update(snap, dt_s)
    if result.old_state != result.new_state:
        log.info("Transition: %s -> %s | %s", result.old_state.value, result.new_state.value, result.reason)
    for d in result.diagnostics:
        log.info("Diagnose: %s | %s | %s", d.severity.value, d.code, d.message)
    return result


def main() -> None:
    xlsx = Path(__file__).with_name("OPCUA_Knotenpunktliste_final.xlsx")
    if not xlsx.exists():
        xlsx = Path("OPCUA_Knotenpunktliste_final.xlsx")
    repo = ExcelNodeRepository(xlsx)
    log.info("FSM-relevante Knoten geladen: %d", len(repo.required_for_fsm()))

    # Simulation nutzt dieselben API-Namen wie der reale OPC-UA-Reader.
    fsm = BrewStateMachine()

    log.info("=== Normaler Ablauf mit Excel-basierten Signalnamen ===")
    run_step(fsm, make_values(k2_fuellstand=10, k2_temperatur=65), 0, start=True)
    run_step(fsm, make_values(k2_temperatur=65), 3600)
    run_step(fsm, make_values(durchfluss_nachguss_maische=2), 3600)
    run_step(fsm, make_values(k2_temperatur=110), 3600)
    run_step(fsm, make_values(mobiler_sensor_temperatur=24), 0)
    run_step(fsm, make_values(mobiler_sensor_temperatur=20), 3600)
    log.info("Endzustand: %s", fsm.state.value)

    """
    log.info("=== Safety: Not-Aus führt zu EMERGENCY ===")
    fsm2 = BrewStateMachine()
    run_step(fsm2, make_values(), 0, start=True)
    run_step(fsm2, make_values(k2_temperatur=65), 0, e_stop=True)
    run_step(fsm2, make_values(k2_temperatur=65), 0, ack=True)
    log.info("Endzustand: %s", fsm2.state.value)
    """

    """
    log.info("=== Prozessfehler: Soll-/Ist-Abweichung führt zu ERROR ===")
    fsm3 = BrewStateMachine()
    run_step(fsm3, make_values(k2_temperatur=65), 0, start=True)
    # Extrem hoch, aber unterhalb absoluter EMERGENCY-Grenze: Prozessfehler.
    run_step(fsm3, make_values(k2_temperatur=90), 0)
    run_step(fsm3, make_values(k2_temperatur=65), 0, ack=True)
    log.info("Endzustand: %s", fsm3.state.value)

    # Beispiel Collector: in Echtbetrieb ersetzt SimulatedNodeReader durch PythonOpcUaNodeReader.
    collector = OpcUaCollector(repo, SimulatedNodeReader(make_values()))
    opc_values = collector.read_process_values()
    log.info("Collector-Beispielwerte: %s", {k: opc_values[k] for k in sorted(opc_values)[:5]})
    """

if __name__ == "__main__":
    main()