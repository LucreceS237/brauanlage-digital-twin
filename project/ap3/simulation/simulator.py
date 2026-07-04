"""
File: simulator.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: project presentation.
"""
from __future__ import annotations

from project.shared.simulation import ProcessSimulator

# Backward-compatible alias used by collector_service.
Simulator = ProcessSimulator

__all__ = ["ProcessSimulator", "Simulator"]
