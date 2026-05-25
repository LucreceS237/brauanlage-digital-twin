# transition_log.py
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from states import BrewState

if TYPE_CHECKING:
    from fsm import BrewStateMachine

LOGGER_NAME = "brauanlage.fsm"


def setup_logging(level: int = logging.INFO) -> None:
    """Logging für die Brauanlage konfigurieren (Zeitstempel + Level)."""
    root = logging.getLogger()
    if root.handlers:
        return
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def log_transition(
    fsm: BrewStateMachine,
    old_state: BrewState,
    new_state: BrewState,
) -> None:
    """Zustandswechsel mit Zeitstempel, Guard-Grund und Ausgängen protokollieren."""
    if old_state == new_state:
        return
    logger = logging.getLogger(LOGGER_NAME)
    reason = fsm.last_transition_reason or "unbekannt"
    soll = fsm.temperature_setpoint
    o = fsm.outputs
    logger.info(
        "%s -> %s | Grund: %s | Soll=%s | Heiz=%s Pumpe=%s Ventil=%s",
        old_state.value,
        new_state.value,
        reason,
        soll if soll is not None else "-",
        o.heater_on,
        o.pump_on,
        o.valve_open,
    )
