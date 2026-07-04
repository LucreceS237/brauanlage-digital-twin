"""
File: conftest.py
Work Package: tests
Responsible Engineer: Engineer D
Purpose: Make project packages importable from the tests directory.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND = os.path.join(ROOT, "backend")
AP2_PUBLISHER = os.path.join(ROOT, "project", "ap2", "mqtt_publisher")
for path in (ROOT, BACKEND, AP2_PUBLISHER):
    if path not in sys.path:
        sys.path.insert(0, path)
