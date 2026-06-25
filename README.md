# Brauanlage Digital Twin

## Features

- OPC-UA communication
- Flask REST API
- SQLite database
- Live dashboard
- Docker support
- Anomaly detection

## Overview

This project implements a Digital Twin for an automated brewing system controlled by a Siemens S7-1500 PLC.

The Digital Twin continuously acquires process values from the PLC through OPC-UA, stores them in a local SQLite database, reconstructs the current process state, detects anomalies, and exposes the current system status through a web application.

The project is developed by a team of five System Engineering students.

---

# Project Objectives

The Digital Twin shall:

* Connect to the PLC via OPC-UA.
* Collect process variables in real time.
* Store historical process data.
* Reconstruct the brewing process state.
* Detect abnormal process behavior.
* Provide a web-based visualization interface.
* Support future predictive analytics and process optimization.

---

# Team Responsibilities

## Engineer A – OPC-UA & Process Analysis

Responsible for:

* Identifying relevant PLC variables.
* Mapping NodeIds.
* Validating process variables.
* Defining polling priorities.
* Providing process knowledge for FSM and anomaly detection.

Deliverables:

* OPC-UA node catalogue
* Variable validation report
* Process documentation

---

## Engineer B – Data Acquisition & Storage

Originally responsible for:

* Database design
* OPC-UA collector
* Data persistence layer

As Engineer B left the project, these responsibilities were reassigned.

Deliverables:

* SQLite database
* OPC-UA collector
* Storage layer

---

## Engineer C – Finite State Machine (FSM)

Responsible for:

* Reconstructing brewing process states.
* Implementing process transitions.
* Tracking current process phase.

Examples:

* IDLE
* MASHING
* LAUTERING
* BOILING
* COOLING
* FERMENTING
* FINISHED

Deliverables:

* FSM implementation
* State transition logic

---

## Engineer D – Anomaly Detection

Responsible for:

* Rule-based anomaly detection.
* Alarm generation.
* Process monitoring.

Examples:

* Temperature too high
* Temperature rise too fast
* Unexpected flow
* Data stale
* Sensor value invalid

Deliverables:

* alarm.py
* rules.py
* detector.py
* Unit tests

---

## Engineer E – API & Visualization

Responsible for:

* REST API
* Web application
* User interface
* Alarm visualization

Planned technology:

* FastAPI backend
* Modern web frontend
* Possible implementation using Lovable

Deliverables:

* Web dashboard
* API endpoints
* Visualization of process state and alarms

---

# System Architecture

```text
Siemens S7-1500 PLC
        │
        ▼
     OPC-UA
        │
        ▼
opcua_collector.py
        │
        ▼
SQLite Database
(brewing_data.db)
        │
 ┌──────┼───────────────┐
 │      │               │
 ▼      ▼               ▼
FSM   Anomaly       REST API
(C)  Detection(D)     (E)
 │      │               │
 └──────┴───────┬───────┘
                ▼
          Web Dashboard
```

---

# Database Design

The project uses SQLite because:

* No server installation required.
* Easy setup.
* Portable.
* Suitable for educational projects.

Main tables:

| Table          | Purpose                      |
| -------------- | ---------------------------- |
| data_points    | OPC-UA variable definitions  |
| snapshots      | One polling cycle            |
| measurements   | Individual measurements      |
| process_states | FSM states                   |
| alarms         | Active and historical alarms |
| system_events  | Technical events and errors  |

---

# Project Structure

```text
brauanlage-digital-twin/
│
├── database/
│   └── schema.sql
│
├── data/
│   └── brewing_data.db
│
├── scripts/
│   ├── init_db.py
│   ├── opcua_collector.py
│   └── inspect_latest.py
│
├── src/
│   ├── storage/
│   │   ├── database.py
│   │   └── data_points.py
│   │
│   └── anomaly_detection/
│       ├── alarm.py
│       ├── rules.py
│       └── detector.py
│
├── test/
│   └── test_anomaly_rules.py
│
├── requirements.txt
├── .env.example
└── README.md
```

---

# Description of Important Files

## schema.sql

Creates the SQLite database structure.

Defines:

* data_points
* snapshots
* measurements
* alarms
* process_states
* system_events

---

## data_points.py

Contains the OPC-UA node catalogue.

Provides:

* NodeIds
* Datatypes
* Units
* Validation status
* Polling configuration

Used by:

* OPC-UA collector
* Database initialization

---

## database.py

Database access layer.

Provides:

* Database initialization
* Snapshot storage
* Measurement storage
* Alarm storage
* Retrieval of latest process state

Used by:

* Collector
* FSM
* Anomaly Detection
* API

---

## opcua_collector.py

Connects to the PLC.

Responsibilities:

* Read OPC-UA values.
* Create snapshots.
* Store measurements.
* Handle reconnects.

---

## alarm.py

Defines the standard alarm model.

Used by:

* rules.py
* detector.py
* API

---

## rules.py

Contains individual anomaly detection rules.

Examples:

* TEMP_TOO_HIGH
* TEMP_TOO_LOW
* DATA_STALE
* LOW_FLOW_DURING_LAUTERING

---

## detector.py

Coordinates anomaly detection.

Responsibilities:

* Maintain history
* Execute rules
* Manage active alarms

---

## inspect_latest.py

Debugging tool.

Displays the latest Digital Twin snapshot.

---

# How the Project Works

Step 1

Initialize the database.

```bash
python scripts/init_db.py
```

Step 2

Start the OPC-UA collector.

```bash
python scripts/opcua_collector.py
```

The collector:

* Connects to the PLC.
* Reads process values.
* Stores snapshots.

Step 3

Verify incoming data.

```bash
python scripts/inspect_latest.py
```

Step 4

FSM uses latest snapshot.

```python
snapshot = db.get_latest_snapshot()
```

Step 5

Anomaly detector evaluates the snapshot.

```python
alarms = detector.update(snapshot)
```

Step 6

Alarms are stored in the database.

```python
db.insert_alarm(...)
```

Step 7

API and Web Dashboard display:

* Current process state
* Live measurements
* Active alarms

---

# Installation

Create virtual environment:

```bash
python -m venv .venv
```

Activate:

Windows

```bash
.venv\Scripts\activate
```

Linux/Mac

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Configuration

Create a .env file from the template:

```bash
copy .env.example .env
```

Example:

```env
OPCUA_SERVER_URL=opc.tcp://192.168.0.1:4840
DATABASE_PATH=data/brewing_data.db
DYNAMIC_POLL_INTERVAL_SECONDS=1
CONTEXT_POLL_INTERVAL_SECONDS=60
```

---

# Running the Project

Initialize database:

```bash
python scripts/init_db.py
```

Start collector:

```bash
python scripts/opcua_collector.py
```

Inspect latest snapshot:

```bash
python scripts/inspect_latest.py
```

Run anomaly detection tests:

```bash
python -m pytest test -v
```

---

# Current Status

Implemented:

* SQLite database design
* OPC-UA data point catalogue
* Storage layer
* Alarm model
* Rule-based anomaly detection
* Detector orchestration
* Unit testing

In Progress:

* FSM implementation (Engineer C)

Planned:

* REST API
* Web Dashboard
* Alarm visualization
* Process visualization
* Historical trend charts

---

# Future Work

* OPC-UA subscriptions instead of polling
* Historical analytics
* Predictive maintenance
* Process optimization
* Machine learning anomaly detection
* Advanced dashboarding

---

# License

Academic project developed within the System Engineering program.
```bash
pip install -r requirements.txt
python app.py

# Mini Concept

Im Rahmen des Projekts wird ein digitaler Zwilling einer Brauanlage erstellt.

Architecture:

OPC-UA → Flask Backend → SQLite → REST API → Dashboard
