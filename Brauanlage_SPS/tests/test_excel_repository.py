from __future__ import annotations

from pathlib import Path

from excel_node_repository import ExcelNodeRepository
from signal_model import NodePriority


def test_repository_loads_top_nodes():
    repo = ExcelNodeRepository(Path(__file__).resolve().parents[1] / "OPCUA_Knotenpunktliste_final.xlsx")
    nodes = repo.required_for_fsm()
    assert "aktueller_schritt" in nodes
    assert "durchfluss_nachguss_maische" in nodes
    assert "k2_temperatur" in nodes
    assert nodes["aktueller_schritt"].node_id.startswith("ns=3;")


def test_colored_nodes_are_classified():
    repo = ExcelNodeRepository(Path(__file__).resolve().parents[1] / "OPCUA_Knotenpunktliste_final.xlsx")
    nodes = repo.load()
    assert nodes["aktueller_schritt"].priority is NodePriority.TOP_PFLICHT
    assert nodes["k2_temperatur_sollwert_obere_grenze"].priority is NodePriority.PARAMETER_LIMIT
    assert nodes["k3_fuellstand"].priority is NodePriority.NEEDS_REVIEW