"""
File: main.py
Work Package: backend
Responsible Engineer: Engineer D
Purpose: FastAPI entry point. Wires AP3 (storage/MQTT/API), AP4 (via AP5) and AP6 (frontend consumer). Keeps only startup/shutdown and router registration here.
"""
from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Ensure repo root is on PYTHONPATH so `project.*` imports resolve in Docker/local.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from project.ap3.api import (
    alarm_routes,
    connection_routes,
    logbook_routes,
    session_routes,
    simulation_routes,
    status_routes,
)
from project.ap3.config import settings
from project.ap3.database import mongodb
from project.ap3.database.seed_data_points import seed_all
from project.ap3.services import collector_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongodb.connect()
    await mongodb.init_collections()
    seeded = await seed_all()
    logger.info("Startup complete. Seeded: %s", seeded)
    yield
    try:
        if collector_service.runtime.active:
            await collector_service.stop(delete_runtime=False)
    except Exception:  # noqa: BLE001
        logger.warning("Error stopping collector on shutdown", exc_info=True)
    await mongodb.disconnect()


app = FastAPI(
    title="Digital Brewing System",
    description="Digital twin backend (AP3 storage, AP4 FSM via AP5, MQTT real-SPS path).",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(connection_routes.router)
app.include_router(session_routes.router)
app.include_router(simulation_routes.router)
app.include_router(status_routes.router)
app.include_router(alarm_routes.router)
app.include_router(logbook_routes.router)


@app.get("/")
async def root():
    return {"name": "Digital Brewing System", "docs": "/docs", "health": "/health"}


@app.get("/health")
async def health():
    return {"status": "ok", "simulationEnabled": settings.enable_simulation_mode}
