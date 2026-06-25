from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from excel_node_repository import ExcelNodeRepository
from signal_model import NodeDefinition

log = logging.getLogger(__name__)


class OpcUaReadError(RuntimeError):
    pass


class NodeReader(ABC):
    """Port/Interface nach SOLID: FSM kennt nur dieses Interface, nicht asyncua."""

    @abstractmethod
    def read_values(self, node_defs: dict[str, NodeDefinition]) -> dict[str, Any]:
        raise NotImplementedError


class SimulatedNodeReader(NodeReader):
    """Deterministische Simulation für Tests, Demo und Offline-Entwicklung."""

    def __init__(self, values: dict[str, Any] | None = None) -> None:
        self.values = values or {}

    def read_values(self, node_defs: dict[str, NodeDefinition]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for api_name, nd in node_defs.items():
            result[api_name] = self.values.get(api_name, self._default_value(nd))
        return result

    @staticmethod
    def _default_value(nd: NodeDefinition) -> Any:
        dtype = (nd.datatype or "").lower()
        if "bool" in dtype:
            return False
        if any(x in dtype for x in ("float", "real", "double")):
            return 0.0
        if "int" in dtype or "time" in dtype:
            return 0
        return ""


class PythonOpcUaNodeReader(NodeReader):
    """Realistischer OPC-UA-Reader für Siemens/OPC-UA.

    Erwartet das Paket `opcua` (python-opcua):
        pip install opcua

    Das Projekt liest ausschließlich read-only Knoten. Schreibzugriffe werden
    absichtlich nicht implementiert, weil die Excel-Tabelle den Projektzugriff
    als read-only dokumentiert.
    """

    def __init__(self, endpoint: str, timeout_s: float = 4.0) -> None:
        self.endpoint = endpoint
        self.timeout_s = timeout_s
        self._client = None
        self._node_cache: dict[str, Any] = {}

    def connect(self) -> None:
        try:
            from opcua import Client  # type: ignore
        except ImportError as exc:
            raise OpcUaReadError("Paket 'opcua' fehlt. Installiere mit: pip install opcua") from exc
        self._client = Client(self.endpoint, timeout=self.timeout_s)
        self._client.connect()
        log.info("OPC-UA verbunden: %s", self.endpoint)

    def disconnect(self) -> None:
        if self._client is not None:
            self._client.disconnect()
            self._client = None
            self._node_cache.clear()
            log.info("OPC-UA getrennt")

    def read_values(self, node_defs: dict[str, NodeDefinition]) -> dict[str, Any]:
        if self._client is None:
            self.connect()
        assert self._client is not None
        result: dict[str, Any] = {}
        for api_name, nd in node_defs.items():
            try:
                node = self._node_cache.get(api_name)
                if node is None:
                    node = self._client.get_node(nd.node_id)
                    self._node_cache[api_name] = node
                result[api_name] = node.get_value()
            except Exception as exc:  # pragma: no cover - abhängig von SPS/Netz
                raise OpcUaReadError(f"Lesefehler bei {api_name} ({nd.node_id}): {exc}") from exc
        return result


class OpcUaCollector:
    """Application Service: liest Knotenliste + OPC-Werte und gibt Dict zurück."""

    def __init__(self, repository: ExcelNodeRepository, reader: NodeReader) -> None:
        self.repository = repository
        self.reader = reader

    def read_process_values(self) -> dict[str, Any]:
        node_defs = self.repository.required_for_fsm()
        return self.reader.read_values(node_defs)