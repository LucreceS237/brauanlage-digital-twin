"""
File: serialization.py
Work Package: AP3
Responsible Engineer: Engineer A, Engineer D (Engineer B left)
Purpose: MongoDB documents contain types that are not directly JSON serialisable by FastAPI's default encoder in the shape we want (ObjectId, datetime). This helper normalises a document: it stringifies the _id into "id" and converts datetimes to ISO-8601 strings, recursively. Keeping this in one place avoids repeating the conversion in every route.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any


def _convert(value: Any) -> Any:
    """Recursively convert a single value into a JSON-friendly form."""
    # Imported here so bson is only required when actually serialising.
    from bson import ObjectId

    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _convert(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_convert(v) for v in value]
    return value


def clean_doc(doc: dict | None) -> dict | None:
    """Return a JSON-serialisable copy of a Mongo document (or None)."""
    if doc is None:
        return None
    out: dict[str, Any] = {}
    for key, value in doc.items():
        if key == "_id":
            out["id"] = str(value)
            continue
        out[key] = _convert(value)
    return out
