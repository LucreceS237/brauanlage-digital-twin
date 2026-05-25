from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path

from excel_node_repository import ExcelNodeRepository
from fsm import BrewStateMachine
from opcua_client import OpcUaCollector, PythonOpcUaNodeReader, SimulatedNodeReader
from process_snapshot import ProcessSnapshot

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("brauanlage.main")


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Digitaler Zwilling / FSM der Labor-Brauanlage")
    parser.add_argument("--xlsx", default="OPCUA_Knotenpunktliste_final.xlsx", help="Pfad zur AP1-OPC-UA-Knotenliste")
    parser.add_argument("--endpoint", default="opc.tcp://localhost:4840", help="OPC-UA Endpoint der Siemens SPS")
    parser.add_argument("--simulate", action="store_true", help="Ohne SPS mit Simulationswerten starten")
    parser.add_argument("--cycle", type=float, default=1.0, help="Zykluszeit in Sekunden")
    return parser


def main() -> None:
    args = build_argparser().parse_args()
    repo = ExcelNodeRepository(Path(args.xlsx))

    if args.simulate:
        reader = SimulatedNodeReader({
            "aktueller_schritt": 0,
            "durchfluss_nachguss_maische": 1.0,
            "k1_temperatur": 22.0,
            "k2_temperatur": 65.0,
            "k2_fuellstand": 10.0,
            "k2_fuellstand_voll": True,
            "k3_temperatur": 70.0,
            "k3_fuellstand": 20.0,
            "k3_maximaler_fuellstand": 50.0,
            "k3_minimaler_fuellstand": 6.0,
            "mobiler_sensor_temperatur": 20.0,
        })
    else:
        reader = PythonOpcUaNodeReader(args.endpoint)

    collector = OpcUaCollector(repo, reader)
    fsm = BrewStateMachine()
    start_sent = False

    try:
        while True:
            values = collector.read_process_values()
            snapshot = ProcessSnapshot.from_opc_values(values, start_requested=not start_sent)
            start_sent = True
            result = fsm.update(snapshot, dt_s=args.cycle)
            log.info("STATE=%s reason=%s diagnostics=%d", result.new_state.value, result.reason, len(result.diagnostics))
            time.sleep(args.cycle)
    except KeyboardInterrupt:
        log.info("Beendet durch Benutzer")
    finally:
        if hasattr(reader, "disconnect"):
            reader.disconnect()


if __name__ == "__main__":
    main()